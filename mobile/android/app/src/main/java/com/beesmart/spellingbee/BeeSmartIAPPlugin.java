package com.beesmart.spellingbee;

import android.app.Activity;
import android.util.Log;

import androidx.annotation.NonNull;

import com.android.billingclient.api.AcknowledgePurchaseParams;
import com.android.billingclient.api.PendingPurchasesParams;
import com.android.billingclient.api.BillingClient;
import com.android.billingclient.api.BillingClientStateListener;
import com.android.billingclient.api.BillingFlowParams;
import com.android.billingclient.api.BillingResult;
import com.android.billingclient.api.ProductDetails;
import com.android.billingclient.api.Purchase;
import com.android.billingclient.api.PurchasesUpdatedListener;
import com.android.billingclient.api.QueryProductDetailsParams;
import com.android.billingclient.api.QueryPurchasesParams;
import com.getcapacitor.JSArray;
import com.getcapacitor.JSObject;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.annotation.CapacitorPlugin;

import android.content.SharedPreferences;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;

@CapacitorPlugin(name = "BeeSmartIAP")
public class BeeSmartIAPPlugin extends Plugin implements PurchasesUpdatedListener {

    private static final String PREFS_INSTALL_ID = "beesmart_install_id_v1";

    private static final String TAG = "BILLING";

    private BillingClient billingClient;
    private volatile boolean ready = false;
    private volatile boolean connecting = false;

    private PluginCall pendingPurchaseCall;
    private String pendingPurchaseProductId;

    @Override
    public void load() {
        super.load();

        billingClient = BillingClient.newBuilder(getContext())
            .setListener(this)
            .enablePendingPurchases(PendingPurchasesParams.newBuilder().enableOneTimeProducts().build())
            .enableAutoServiceReconnection()
            .build();

        connectIfNeeded(null);
    }

    private void connectIfNeeded(final Runnable afterConnected) {
        if (billingClient == null) return;
        if (ready) {
            if (afterConnected != null) afterConnected.run();
            return;
        }
        if (connecting) {
            Log.d(TAG, "already connecting — queuing callback");
            new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(() -> connectIfNeeded(afterConnected), 500);
            return;
        }
        connecting = true;
        billingClient.startConnection(new BillingClientStateListener() {
            @Override
            public void onBillingSetupFinished(@NonNull BillingResult billingResult) {
                connecting = false;
                ready = billingResult.getResponseCode() == BillingClient.BillingResponseCode.OK;
                Log.d(TAG, "setup code=" + billingResult.getResponseCode() + ", msg=" + billingResult.getDebugMessage() + ", ready=" + ready);
                if (ready && afterConnected != null) afterConnected.run();
            }

            @Override
            public void onBillingServiceDisconnected() {
                connecting = false;
                ready = false;
                Log.d(TAG, "service disconnected — auto-reconnect will retry");
            }
        });
    }

    private String friendlyError(int code, String debugMsg) {
        switch (code) {
            case BillingClient.BillingResponseCode.SERVICE_UNAVAILABLE:
                return "Billing not ready — check your internet connection and Google Play account.";
            case BillingClient.BillingResponseCode.BILLING_UNAVAILABLE:
                return "Google Play Billing is unavailable on this device.";
            case BillingClient.BillingResponseCode.ITEM_ALREADY_OWNED:
                return "Purchase already owned — use Restore Purchases.";
            case BillingClient.BillingResponseCode.ITEM_NOT_OWNED:
                return "This item is not owned by your account.";
            case BillingClient.BillingResponseCode.ITEM_UNAVAILABLE:
                return "No products found — check product IDs in Play Console.";
            case BillingClient.BillingResponseCode.DEVELOPER_ERROR:
                return "Developer error — product ID or base plan may be inactive.";
            case BillingClient.BillingResponseCode.NETWORK_ERROR:
                return "Network error — please check your connection and try again.";
            default:
                return "Billing error (" + code + "): " + debugMsg;
        }
    }

    @PluginMethod
    public void getInstallId(final PluginCall call) {
        SharedPreferences prefs = getContext().getSharedPreferences(PREFS_INSTALL_ID, 0);
        String installId = prefs.getString("installId", null);
        if (installId == null || installId.length() < 12) {
            installId = UUID.randomUUID().toString();
            prefs.edit().putString("installId", installId).apply();
        }
        JSObject out = new JSObject();
        out.put("installId", installId);
        call.resolve(out);
    }

    /**
     * restorePurchases — queries Google Play for all PURCHASED subscriptions and in-app purchases.
     * Returns isPremiumActive=true if any active subscription is found.
     * The web layer (native-iap-bridge.js) uses the returned subscriptions array to verify
     * tokens server-side and apply entitlements.
     */
    @PluginMethod
    public void restorePurchases(final PluginCall call) {
        Log.d(TAG, "restorePurchases called");
        connectIfNeeded(() -> {
            final JSArray restoredSubs = new JSArray();
            final JSArray restoredInapp = new JSArray();
            final boolean[] isPremium = {false};

            QueryPurchasesParams subsParams = QueryPurchasesParams.newBuilder()
                .setProductType(BillingClient.ProductType.SUBS)
                .build();

            billingClient.queryPurchasesAsync(subsParams, (result1, subsList) -> {
                if (result1.getResponseCode() != BillingClient.BillingResponseCode.OK) {
                    Log.e(TAG, "restore subs query failed: " + result1.getDebugMessage());
                    call.reject(friendlyError(result1.getResponseCode(), result1.getDebugMessage()));
                    return;
                }

                for (Purchase p : subsList) {
                    if (p.getPurchaseState() != Purchase.PurchaseState.PURCHASED) continue;
                    isPremium[0] = true;
                    Log.d(TAG, "restore: found active sub token=" + p.getPurchaseToken());
                    for (String pid : p.getProducts()) {
                        try {
                            JSObject o = new JSObject();
                            o.put("productId", pid);
                            o.put("purchaseToken", p.getPurchaseToken());
                            o.put("orderId", p.getOrderId());
                            o.put("acknowledged", p.isAcknowledged());
                            o.put("purchaseState", p.getPurchaseState());
                            restoredSubs.put(o);
                        } catch (Exception ignored) {}
                    }
                    // Auto-acknowledge unacknowledged active purchases
                    if (!p.isAcknowledged()) {
                        AcknowledgePurchaseParams ack = AcknowledgePurchaseParams.newBuilder()
                            .setPurchaseToken(p.getPurchaseToken()).build();
                        billingClient.acknowledgePurchase(ack, br ->
                            Log.d(TAG, "restore ack result: " + br.getResponseCode()));
                    }
                }

                QueryPurchasesParams inappParams = QueryPurchasesParams.newBuilder()
                    .setProductType(BillingClient.ProductType.INAPP)
                    .build();

                billingClient.queryPurchasesAsync(inappParams, (result2, inappList) -> {
                    if (result2.getResponseCode() == BillingClient.BillingResponseCode.OK) {
                        for (Purchase p : inappList) {
                            if (p.getPurchaseState() != Purchase.PurchaseState.PURCHASED) continue;
                            for (String pid : p.getProducts()) {
                                try {
                                    JSObject o = new JSObject();
                                    o.put("productId", pid);
                                    o.put("purchaseToken", p.getPurchaseToken());
                                    o.put("orderId", p.getOrderId());
                                    o.put("acknowledged", p.isAcknowledged());
                                    o.put("purchaseState", p.getPurchaseState());
                                    restoredInapp.put(o);
                                } catch (Exception ignored) {}
                            }
                        }
                    }

                    Log.d(TAG, "restorePurchases complete — isPremium=" + isPremium[0]);
                    JSObject out = new JSObject();
                    out.put("success", true);
                    out.put("isPremiumActive", isPremium[0]);
                    out.put("subscriptions", restoredSubs);
                    out.put("inapp", restoredInapp);
                    call.resolve(out);
                });
            });
        });
    }

    @PluginMethod
    public void getOwnedProducts(final PluginCall call) {
        connectIfNeeded(() -> {
            final Set<String> productIds = new HashSet<>();
            final JSArray subsPurchases = new JSArray();
            final JSArray inappPurchases = new JSArray();

            QueryPurchasesParams subsParams = QueryPurchasesParams.newBuilder()
                .setProductType(BillingClient.ProductType.SUBS)
                .build();

            billingClient.queryPurchasesAsync(subsParams, (billingResult, purchasesList) -> {
                if (billingResult.getResponseCode() != BillingClient.BillingResponseCode.OK) {
                    Log.e(TAG, "getOwnedProducts subs failed: " + billingResult.getDebugMessage());
                    call.reject(friendlyError(billingResult.getResponseCode(), billingResult.getDebugMessage()));
                    return;
                }

                for (Purchase p : purchasesList) {
                    if (p.getPurchaseState() != Purchase.PurchaseState.PURCHASED) continue;
                    productIds.addAll(p.getProducts());
                    try {
                        if (p.getProducts() != null) {
                            for (String pid : p.getProducts()) {
                                JSObject o = new JSObject();
                                o.put("productId", pid);
                                o.put("purchaseToken", p.getPurchaseToken());
                                o.put("orderId", p.getOrderId());
                                o.put("acknowledged", p.isAcknowledged());
                                o.put("purchaseState", p.getPurchaseState());
                                subsPurchases.put(o);
                            }
                        }
                    } catch (Exception ignored) {}
                }

                QueryPurchasesParams inappParams = QueryPurchasesParams.newBuilder()
                    .setProductType(BillingClient.ProductType.INAPP)
                    .build();

                billingClient.queryPurchasesAsync(inappParams, (billingResult2, purchasesList2) -> {
                    if (billingResult2.getResponseCode() != BillingClient.BillingResponseCode.OK) {
                        Log.e(TAG, "getOwnedProducts inapp failed: " + billingResult2.getDebugMessage());
                        call.reject(friendlyError(billingResult2.getResponseCode(), billingResult2.getDebugMessage()));
                        return;
                    }

                    for (Purchase p : purchasesList2) {
                        if (p.getPurchaseState() != Purchase.PurchaseState.PURCHASED) continue;
                        productIds.addAll(p.getProducts());
                        try {
                            if (p.getProducts() != null) {
                                for (String pid : p.getProducts()) {
                                    JSObject o = new JSObject();
                                    o.put("productId", pid);
                                    o.put("purchaseToken", p.getPurchaseToken());
                                    o.put("orderId", p.getOrderId());
                                    o.put("acknowledged", p.isAcknowledged());
                                    o.put("purchaseState", p.getPurchaseState());
                                    inappPurchases.put(o);
                                }
                            }
                        } catch (Exception ignored) {}
                    }

                    JSArray arr = new JSArray();
                    for (String pid : productIds) {
                        arr.put(pid);
                    }

                    boolean hasPremium = subsPurchases.length() > 0;
                    Log.d(TAG, "getOwnedProducts done — productIds=" + arr.length() + " isPremiumActive=" + hasPremium);

                    JSObject out = new JSObject();
                    out.put("productIds", arr);
                    out.put("subscriptions", subsPurchases);
                    out.put("inapp", inappPurchases);
                    out.put("isPremiumActive", hasPremium);
                    call.resolve(out);
                });
            });
        });
    }

    @PluginMethod
    public void purchase(final PluginCall call) {
        final String productId = call.getString("productId");
        if (productId == null || productId.trim().isEmpty()) {
            call.reject("missing_productId");
            return;
        }

        // Only allow one purchase call at a time.
        if (pendingPurchaseCall != null) {
            call.reject("purchase_in_progress");
            return;
        }

        if (!billingClient.isReady()) {
            Log.d(TAG, "purchase called — billing not ready, connecting first");
        }
        connectIfNeeded(() -> queryAndLaunchBillingFlow(call, productId, BillingClient.ProductType.SUBS, true));
    }

    @PluginMethod
    public void getProductDetails(final PluginCall call) {
        final String productId = call.getString("productId");
        if (productId == null || productId.trim().isEmpty()) {
            call.reject("missing_productId");
            return;
        }

        connectIfNeeded(() -> queryAndReturnProductDetails(call, productId, BillingClient.ProductType.SUBS, true));
    }

    private void queryAndReturnProductDetails(final PluginCall call, final String productId, final String productType, final boolean allowFallbackToInapp) {
        List<QueryProductDetailsParams.Product> products = Arrays.asList(
            QueryProductDetailsParams.Product.newBuilder()
                .setProductId(productId)
                .setProductType(productType)
                .build()
        );

        QueryProductDetailsParams params = QueryProductDetailsParams.newBuilder()
            .setProductList(products)
            .build();

        billingClient.queryProductDetailsAsync(params, (billingResult, queryResult) -> {
            if (billingResult.getResponseCode() != BillingClient.BillingResponseCode.OK) {
                Log.e(TAG, "getProductDetails failed: " + billingResult.getDebugMessage());
                call.reject(friendlyError(billingResult.getResponseCode(), billingResult.getDebugMessage()));
                return;
            }

            List<ProductDetails> productDetailsList = queryResult.getProductDetailsList();
            if (productDetailsList == null || productDetailsList.isEmpty()) {
                if (allowFallbackToInapp && BillingClient.ProductType.SUBS.equals(productType)) {
                    queryAndReturnProductDetails(call, productId, BillingClient.ProductType.INAPP, false);
                    return;
                }
                Log.e(TAG, "product_not_found: " + productType + ":" + productId);
                call.reject(friendlyError(BillingClient.BillingResponseCode.ITEM_UNAVAILABLE, productId));
                return;
            }

            Log.d(TAG, "getProductDetails found: " + productId);
            ProductDetails details = productDetailsList.get(0);

            JSObject out = new JSObject();
            out.put("productId", productId);
            out.put("productType", productType);
            try { out.put("title", details.getTitle()); } catch (Exception ignored) {}
            try { out.put("description", details.getDescription()); } catch (Exception ignored) {}

            // Subscription pricing (best-effort: first offer, first phase)
            if (BillingClient.ProductType.SUBS.equals(productType)) {
                try {
                    List<ProductDetails.SubscriptionOfferDetails> offers = details.getSubscriptionOfferDetails();
                    if (offers != null && !offers.isEmpty() && offers.get(0) != null) {
                        ProductDetails.SubscriptionOfferDetails offer = offers.get(0);
                        try { out.put("offerToken", offer.getOfferToken()); } catch (Exception ignored) {}

                        ProductDetails.PricingPhases phases = offer.getPricingPhases();
                        if (phases != null && phases.getPricingPhaseList() != null && !phases.getPricingPhaseList().isEmpty()) {
                            // Return all phases so the web UI can show free trial + recurring price.
                            JSArray phasesArr = new JSArray();
                            for (ProductDetails.PricingPhase phase : phases.getPricingPhaseList()) {
                                JSObject ph = new JSObject();
                                try { ph.put("formattedPrice", phase.getFormattedPrice()); } catch (Exception ignored) {}
                                try { ph.put("billingPeriod", phase.getBillingPeriod()); } catch (Exception ignored) {}
                                try { ph.put("priceCurrencyCode", phase.getPriceCurrencyCode()); } catch (Exception ignored) {}
                                try { ph.put("priceAmountMicros", String.valueOf(phase.getPriceAmountMicros())); } catch (Exception ignored) {}
                                try { ph.put("recurrenceMode", phase.getRecurrenceMode()); } catch (Exception ignored) {}
                                phasesArr.put(ph);
                            }
                            out.put("pricingPhases", phasesArr);

                            // Convenience: also include the first phase fields for simple callers.
                            ProductDetails.PricingPhase phase0 = phases.getPricingPhaseList().get(0);
                            try { out.put("formattedPrice", phase0.getFormattedPrice()); } catch (Exception ignored) {}
                            try { out.put("billingPeriod", phase0.getBillingPeriod()); } catch (Exception ignored) {}
                            try { out.put("priceCurrencyCode", phase0.getPriceCurrencyCode()); } catch (Exception ignored) {}
                            try { out.put("priceAmountMicros", String.valueOf(phase0.getPriceAmountMicros())); } catch (Exception ignored) {}
                            try { out.put("recurrenceMode", phase0.getRecurrenceMode()); } catch (Exception ignored) {}
                        }
                    }
                } catch (Exception ignored) {}
            } else {
                // In-app pricing (one-time)
                try {
                    ProductDetails.OneTimePurchaseOfferDetails one = details.getOneTimePurchaseOfferDetails();
                    if (one != null) {
                        try { out.put("formattedPrice", one.getFormattedPrice()); } catch (Exception ignored) {}
                        try { out.put("priceCurrencyCode", one.getPriceCurrencyCode()); } catch (Exception ignored) {}
                        try { out.put("priceAmountMicros", String.valueOf(one.getPriceAmountMicros())); } catch (Exception ignored) {}
                    }
                } catch (Exception ignored) {}
            }

            call.resolve(out);
        });
    }

    private void queryAndLaunchBillingFlow(final PluginCall call, final String productId, final String productType, final boolean allowFallbackToInapp) {
        List<QueryProductDetailsParams.Product> products = Arrays.asList(
            QueryProductDetailsParams.Product.newBuilder()
                .setProductId(productId)
                .setProductType(productType)
                .build()
        );

        QueryProductDetailsParams params = QueryProductDetailsParams.newBuilder()
            .setProductList(products)
            .build();

        billingClient.queryProductDetailsAsync(params, (billingResult, queryResult) -> {
            if (billingResult.getResponseCode() != BillingClient.BillingResponseCode.OK) {
                Log.e(TAG, "queryAndLaunchBillingFlow failed: " + billingResult.getDebugMessage());
                call.reject(friendlyError(billingResult.getResponseCode(), billingResult.getDebugMessage()));
                return;
            }

            List<ProductDetails> productDetailsList = queryResult.getProductDetailsList();
            if (productDetailsList == null || productDetailsList.isEmpty()) {
                if (allowFallbackToInapp && BillingClient.ProductType.SUBS.equals(productType)) {
                    queryAndLaunchBillingFlow(call, productId, BillingClient.ProductType.INAPP, false);
                    return;
                }
                Log.e(TAG, "product not found for purchase: " + productId);
                call.reject(friendlyError(BillingClient.BillingResponseCode.ITEM_UNAVAILABLE, productId));
                return;
            }

            ProductDetails details = productDetailsList.get(0);

            BillingFlowParams.ProductDetailsParams.Builder pdp = BillingFlowParams.ProductDetailsParams.newBuilder()
                .setProductDetails(details);

            if (BillingClient.ProductType.SUBS.equals(productType)) {
                // Choose the first offer token.
                List<ProductDetails.SubscriptionOfferDetails> offers = details.getSubscriptionOfferDetails();
                if (offers != null && !offers.isEmpty() && offers.get(0) != null) {
                    String offerToken = offers.get(0).getOfferToken();
                    if (offerToken != null) {
                        pdp.setOfferToken(offerToken);
                    }
                }
            }

            List<BillingFlowParams.ProductDetailsParams> productDetailsParamsList = new ArrayList<>();
            productDetailsParamsList.add(pdp.build());

            BillingFlowParams flowParams = BillingFlowParams.newBuilder()
                .setProductDetailsParamsList(productDetailsParamsList)
                .build();

            Activity activity = getActivity();
            if (activity == null) {
                call.reject("no_activity");
                return;
            }

            pendingPurchaseCall = call;
            pendingPurchaseProductId = productId;

            Log.d(TAG, "launching billing flow for: " + productId);
            BillingResult launchResult = billingClient.launchBillingFlow(activity, flowParams);
            if (launchResult.getResponseCode() != BillingClient.BillingResponseCode.OK) {
                pendingPurchaseCall = null;
                pendingPurchaseProductId = null;
                Log.e(TAG, "launchBillingFlow failed: " + launchResult.getDebugMessage());
                call.reject(friendlyError(launchResult.getResponseCode(), launchResult.getDebugMessage()));
            }
        });
    }

    @Override
    public void onPurchasesUpdated(@NonNull BillingResult billingResult, List<Purchase> purchases) {
        PluginCall call = pendingPurchaseCall;
        String requestedProductId = pendingPurchaseProductId;

        if (call == null) {
            return;
        }

        // Reset pending state early to prevent re-entrancy issues.
        pendingPurchaseCall = null;
        pendingPurchaseProductId = null;

        int code = billingResult.getResponseCode();
        if (code == BillingClient.BillingResponseCode.USER_CANCELED) {
            JSObject out = new JSObject();
            out.put("productId", requestedProductId);
            out.put("cancelled", true);
            call.resolve(out);
            return;
        }

        if (code != BillingClient.BillingResponseCode.OK || purchases == null || purchases.isEmpty()) {
            Log.e(TAG, "onPurchasesUpdated failed: code=" + code + " msg=" + billingResult.getDebugMessage());
            call.reject(friendlyError(code, billingResult.getDebugMessage()));
            return;
        }

        // Resolve with the first matching purchase.
        Purchase selected = purchases.get(0);
        if (requestedProductId != null) {
            for (Purchase p : purchases) {
                if (p.getProducts() != null && p.getProducts().contains(requestedProductId)) {
                    selected = p;
                    break;
                }
            }
        }

        final Purchase chosen = selected;

        // Acknowledge if required.
        if (chosen.getPurchaseState() == Purchase.PurchaseState.PURCHASED && !chosen.isAcknowledged()) {
            AcknowledgePurchaseParams ack = AcknowledgePurchaseParams.newBuilder()
                .setPurchaseToken(chosen.getPurchaseToken())
                .build();

            billingClient.acknowledgePurchase(ack, br -> {
                // Best-effort; still resolve the purchase either way.
                resolvePurchase(call, chosen);
            });
        } else {
            resolvePurchase(call, chosen);
        }
    }

    private void resolvePurchase(final PluginCall call, final Purchase purchase) {
        JSArray productsArr = new JSArray();
        if (purchase.getProducts() != null) {
            for (String pid : purchase.getProducts()) {
                productsArr.put(pid);
            }
        }

        JSObject payload = new JSObject();
        payload.put("purchaseToken", purchase.getPurchaseToken());
        payload.put("orderId", purchase.getOrderId());
        payload.put("products", productsArr);
        payload.put("originalJson", purchase.getOriginalJson());

        JSObject out = new JSObject();
        out.put("productId", (purchase.getProducts() != null && !purchase.getProducts().isEmpty()) ? purchase.getProducts().get(0) : null);
        out.put("purchaseToken", purchase.getPurchaseToken());
        out.put("orderId", purchase.getOrderId());
        out.put("payload", payload);
        call.resolve(out);
    }
}
