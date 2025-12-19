import Foundation
import Capacitor
import StoreKit

// Native IAP bridge for the BeeSmart web UI.
// Exposes a minimal API used by templates:
// - getOwnedProducts() -> productIds
// - purchase({productId}) -> purchase result (includes JWS when available)
@objc(BeeSmartIAPPlugin)
public class BeeSmartIAPPlugin: CAPPlugin {

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

                call.resolve([
                    "productIds": deduped,
                    "owned": owned
                ])
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
            Task {
                do {
                    let products = try await Product.products(for: [productId])
                    guard let product = products.first else {
                        call.reject("product_not_found")
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
