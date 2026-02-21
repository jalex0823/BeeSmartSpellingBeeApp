import Foundation
import Capacitor
import StoreKit

// NOTE: This plugin is intentionally minimal and review-friendly.
// It should:
// - trigger a real OS-level restore (AppStore.sync)
// - provide a stable device install identifier for best-effort continuity across reinstalls

// Native IAP bridge for the BeeSmart web UI.
//
// IMPORTANT: We explicitly register/export this plugin with the JS name `BeeSmartIAP`
// so it shows up as `window.Capacitor.Plugins.BeeSmartIAP` inside the iOS Capacitor wrapper.
// The web layer then wraps it as `window.BeeSmartIAP`.
//
// Capacitor v5 plugin export.
@objc(BeeSmartIAPPlugin)
public class BeeSmartIAPPlugin: CAPPlugin {

    // Persist a stable per-install identifier.
    // This is used by the web layer to associate anonymous restores after reinstall.
    // It is NOT a tracking identifier (it is scoped to this app install).
    private let installIdDefaultsKey = "beesmart_install_id_v1"

    private func getOrCreateInstallId() -> String {
        let defaults = UserDefaults.standard
        if let existing = defaults.string(forKey: installIdDefaultsKey), existing.count >= 12 {
            return existing
        }
        let newId = UUID().uuidString
        defaults.set(newId, forKey: installIdDefaultsKey)
        return newId
    }

    @objc func getInstallId(_ call: CAPPluginCall) {
        let installId = getOrCreateInstallId()
        call.resolve(["installId": installId])
    }

    // Capacitor v5: method export and plugin naming are typically handled via a
    // generated Obj-C bridge file when using the CAP_PLUGIN macro.
    // This Swift-only plugin remains functional and can be registered via
    // `registerPluginInstance(BeeSmartIAPPlugin())` in AppDelegate.

    // Initiate a real platform restore flow.
    // App Review expects tapping a distinct "Restore" control to trigger an OS-level restore/sync.
    @objc func restorePurchases(_ call: CAPPluginCall) {
        if #available(iOS 15.0, *) {
            Task { @MainActor in
                do {
                    try await AppStore.sync()
                    // Always resolve success to avoid the web layer treating
                    // transient StoreKit errors as a "restore did nothing".
                    // The web layer will reconcile with the server and decide
                    // whether entitlements can be applied (login-required).
                    call.resolve(["success": true])
                } catch {
                    // IMPORTANT: Still resolve to allow the web layer to continue
                    // with server reconcile + user-visible guidance.
                    call.resolve([
                        "success": false,
                        "error": "restore_error",
                        "message": error.localizedDescription
                    ])
                }
            }
        } else {
            call.reject("requires_ios_15")
        }
    }

    @objc func getOwnedProducts(_ call: CAPPluginCall) {
        if #available(iOS 15.0, *) {
            Task {
                var productIds: [String] = []
                var owned: [[String: Any]] = []

                for await entitlement in Transaction.currentEntitlements {
                    switch entitlement {
                    case .verified(let transaction):
                        productIds.append(transaction.productID)
                        owned.append([
                            "productId": transaction.productID,
                            "transactionId": String(transaction.id),
                            "purchaseDate": ISO8601DateFormatter().string(from: transaction.purchaseDate)
                        ])
                    case .unverified:
                        continue
                    }
                }

                // De-dupe while preserving order
                var deduped: [String] = []
                var seen = Set<String>()
                for pid in productIds {
                    if !seen.contains(pid) {
                        seen.insert(pid)
                        deduped.append(pid)
                    }
                }

                await MainActor.run {
                    call.resolve([
                        "productIds": deduped,
                        "owned": owned
                    ])
                }
            }
        } else {
            call.reject("requires_ios_15")
        }
    }

    @objc func purchase(_ call: CAPPluginCall) {
        guard let productId = call.getString("productId"), !productId.isEmpty else {
            call.reject("missing_productId")
            return
        }

        if #available(iOS 15.0, *) {
            // Presenting the StoreKit purchase sheet is most reliable when executed on the main actor.
            // This helps prevent intermittent UI presentation issues in WKWebView/Capacitor shells.
            Task { @MainActor in
                do {
                    let products = try await Product.products(for: [productId])
                    guard let product = products.first else {
                        call.reject("product_not_found: \(productId)")
                        return
                    }

                    let result = try await product.purchase()
                    switch result {
                    case .success(let verification):
                        switch verification {
                        case .verified(let transaction):
                            // Finish ASAP to avoid repeated deliveries.
                            await transaction.finish()

                            var payload: [String: Any] = [
                                "productId": transaction.productID,
                                "transactionId": String(transaction.id)
                            ]

                            // StoreKit 2 does not expose a stable JWS string on Transaction across SDK versions.
                            // Use the JSON representation (signed data can be added later via server receipt validation).
                            // Keep the key name stable for the web layer.
                            payload["jws"] = String(data: transaction.jsonRepresentation, encoding: .utf8) ?? ""

                            call.resolve([
                                "productId": transaction.productID,
                                "transactionId": String(transaction.id),
                                "payload": payload
                            ])

                        case .unverified(_, let error):
                            call.reject("unverified_transaction: \(error.localizedDescription)")
                        }

                    case .userCancelled:
                        call.resolve([
                            "productId": productId,
                            "cancelled": true
                        ])

                    case .pending:
                        call.resolve([
                            "productId": productId,
                            "pending": true
                        ])

                    @unknown default:
                        call.reject("purchase_failed")
                    }

                } catch {
                    call.reject("purchase_error: \(error.localizedDescription)")
                }
            }
        } else {
            call.reject("requires_ios_15")
        }
    }
}
