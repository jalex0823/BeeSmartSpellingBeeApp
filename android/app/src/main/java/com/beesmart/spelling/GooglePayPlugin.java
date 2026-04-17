package com.beesmart.spelling;

import android.app.Activity;
import android.content.Intent;
import android.util.Log;

import androidx.activity.result.ActivityResult;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.ActivityCallback;
import com.getcapacitor.annotation.CapacitorPlugin;
import com.google.android.gms.common.api.ApiException;
import com.google.android.gms.tasks.Task;
import com.google.android.gms.wallet.AutoResolveHelper;
import com.google.android.gms.wallet.IsReadyToPayRequest;
import com.google.android.gms.wallet.PaymentData;
import com.google.android.gms.wallet.PaymentDataRequest;
import com.google.android.gms.wallet.PaymentsClient;
import com.google.android.gms.wallet.Wallet;
import com.google.android.gms.wallet.WalletConstants;

import org.json.JSONArray;
import org.json.JSONObject;

/**
 * GooglePayPlugin — Capacitor plugin that bridges Google Pay into the BeeSmart web layer.
 *
 * JS usage (via BeeSmartIAP which already wraps this via the native plugin):
 *   const plugin = Capacitor.Plugins.GooglePayPlugin;
 *   const ready  = await plugin.isReadyToPay();
 *   const result = await plugin.startPayment({ productId: 'premium_monthly', price: '3.99' });
 *
 * The payment token returned by Google Pay is sent to the Flask backend via
 * /api/android/subscription/verify, exactly as the existing BeeSmartIAP flow does.
 *
 * IMPORTANT: Replace GATEWAY and GATEWAY_MERCHANT_ID with your real processor values
 * before submitting to the Play Store. Invalid merchant config is the #1 production
 * failure point for Google Pay integrations.
 */
@CapacitorPlugin(name = "GooglePayPlugin")
public class GooglePayPlugin extends Plugin {

    private static final String TAG = "GooglePayPlugin";
    private static final int LOAD_PAYMENT_DATA_REQUEST_CODE = 991;

    // ── REPLACE these with your real payment gateway values ──────────────────
    private static final String GATEWAY = "example";
    private static final String GATEWAY_MERCHANT_ID = "exampleMerchantId";
    private static final String MERCHANT_NAME = "BeeSmart Spelling";
    // ─────────────────────────────────────────────────────────────────────────

    // Use ENVIRONMENT_TEST during development; switch to ENVIRONMENT_PRODUCTION
    // only after your Google Pay Business Profile is approved.
    private static final int WALLET_ENVIRONMENT = WalletConstants.ENVIRONMENT_TEST;

    private PaymentsClient paymentsClient;
    private PluginCall pendingPaymentCall;

    // ── Lifecycle ─────────────────────────────────────────────────────────────

    @Override
    public void load() {
        paymentsClient = Wallet.getPaymentsClient(
            getActivity(),
            new Wallet.WalletOptions.Builder()
                .setEnvironment(WALLET_ENVIRONMENT)
                .build()
        );
    }

    // ── Plugin methods exposed to JS ──────────────────────────────────────────

    /**
     * isReadyToPay — check whether Google Pay is available on this device.
     *
     * JS: const { available } = await GooglePayPlugin.isReadyToPay();
     */
    @PluginMethod
    public void isReadyToPay(PluginCall call) {
        try {
            IsReadyToPayRequest request = IsReadyToPayRequest.fromJson(
                buildIsReadyToPayRequest().toString()
            );

            Task<Boolean> task = paymentsClient.isReadyToPay(request);
            task.addOnCompleteListener(completedTask -> {
                try {
                    boolean available = completedTask.getResult(ApiException.class);
                    JSObject result = new JSObject();
                    result.put("available", available);
                    call.resolve(result);
                } catch (ApiException e) {
                    Log.e(TAG, "isReadyToPay ApiException", e);
                    JSObject result = new JSObject();
                    result.put("available", false);
                    result.put("error", e.getMessage());
                    call.resolve(result);
                }
            });
        } catch (Exception e) {
            Log.e(TAG, "isReadyToPay error", e);
            call.reject("isReadyToPay failed: " + e.getMessage(), e);
        }
    }

    /**
     * startPayment — launch the Google Pay sheet.
     *
     * JS: const result = await GooglePayPlugin.startPayment({ productId: 'premium_monthly', price: '3.99' });
     * On success result contains: { token, paymentMethodType, email? }
     */
    @PluginMethod
    public void startPayment(PluginCall call) {
        String productId = call.getString("productId", "premium_monthly");
        String price = call.getString("price", "3.99");

        try {
            JSONObject requestJson = buildPaymentDataRequest(price);
            PaymentDataRequest request = PaymentDataRequest.fromJson(requestJson.toString());

            // Save call so we can resolve it in handleActivityResult.
            pendingPaymentCall = call;
            saveCall(call);

            AutoResolveHelper.resolveTask(
                paymentsClient.loadPaymentData(request),
                getActivity(),
                LOAD_PAYMENT_DATA_REQUEST_CODE
            );
        } catch (Exception e) {
            Log.e(TAG, "startPayment error", e);
            call.reject("startPayment failed: " + e.getMessage(), e);
        }
    }

    // ── Activity result handling ───────────────────────────────────────────────

    /**
     * Called by MainActivity.onActivityResult — routes Google Pay response back to JS.
     */
    public void handleActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode != LOAD_PAYMENT_DATA_REQUEST_CODE) return;

        PluginCall savedCall = pendingPaymentCall;
        pendingPaymentCall = null;

        if (savedCall == null) {
            Log.w(TAG, "handleActivityResult: no pending call");
            return;
        }

        switch (resultCode) {
            case Activity.RESULT_OK: {
                PaymentData paymentData = PaymentData.getFromIntent(data);
                if (paymentData == null) {
                    savedCall.reject("Google Pay returned RESULT_OK but PaymentData is null");
                    return;
                }
                try {
                    String paymentJson = paymentData.toJson();
                    JSONObject paymentObj = new JSONObject(paymentJson);
                    JSONObject paymentMethodData = paymentObj.getJSONObject("paymentMethodData");
                    JSONObject tokenizationData = paymentMethodData.getJSONObject("tokenizationData");
                    String token = tokenizationData.getString("token");

                    String email = "";
                    try { email = paymentObj.getString("email"); } catch (Exception ignored) {}

                    JSObject result = new JSObject();
                    result.put("token", token);
                    result.put("paymentMethodType", paymentMethodData.optString("type", "CARD"));
                    result.put("email", email);
                    result.put("rawJson", paymentJson);

                    Log.d(TAG, "Payment success, token obtained");
                    savedCall.resolve(result);
                } catch (Exception e) {
                    Log.e(TAG, "Error parsing PaymentData", e);
                    savedCall.reject("Failed to parse payment result: " + e.getMessage(), e);
                }
                break;
            }

            case Activity.RESULT_CANCELED:
                Log.d(TAG, "Payment cancelled by user");
                JSObject cancelled = new JSObject();
                cancelled.put("cancelled", true);
                savedCall.resolve(cancelled);
                break;

            case AutoResolveHelper.RESULT_ERROR: {
                Log.e(TAG, "Google Pay RESULT_ERROR");
                savedCall.reject("Google Pay returned an error. Check your merchant configuration.");
                break;
            }

            default:
                savedCall.reject("Unexpected Google Pay result code: " + resultCode);
                break;
        }
    }

    // ── Request builders ──────────────────────────────────────────────────────

    private JSONObject buildIsReadyToPayRequest() throws Exception {
        JSONObject req = new JSONObject();
        req.put("apiVersion", 2);
        req.put("apiVersionMinor", 0);

        JSONObject card = new JSONObject();
        card.put("type", "CARD");

        JSONObject params = new JSONObject();
        params.put("allowedAuthMethods", new JSONArray()
            .put("PAN_ONLY")
            .put("CRYPTOGRAM_3DS"));
        params.put("allowedCardNetworks", new JSONArray()
            .put("VISA")
            .put("MASTERCARD")
            .put("AMEX")
            .put("DISCOVER"));
        card.put("parameters", params);

        req.put("allowedPaymentMethods", new JSONArray().put(card));
        return req;
    }

    private JSONObject buildPaymentDataRequest(String price) throws Exception {
        JSONObject req = new JSONObject();
        req.put("apiVersion", 2);
        req.put("apiVersionMinor", 0);

        // Card payment method
        JSONObject cardMethod = new JSONObject();
        cardMethod.put("type", "CARD");

        JSONObject cardParams = new JSONObject();
        cardParams.put("allowedAuthMethods", new JSONArray()
            .put("PAN_ONLY")
            .put("CRYPTOGRAM_3DS"));
        cardParams.put("allowedCardNetworks", new JSONArray()
            .put("VISA")
            .put("MASTERCARD")
            .put("AMEX")
            .put("DISCOVER"));
        cardMethod.put("parameters", cardParams);

        // Tokenization — REPLACE gateway/gatewayMerchantId with real values
        JSONObject tokenSpec = new JSONObject();
        tokenSpec.put("type", "PAYMENT_GATEWAY");
        JSONObject tokenParams = new JSONObject();
        tokenParams.put("gateway", GATEWAY);
        tokenParams.put("gatewayMerchantId", GATEWAY_MERCHANT_ID);
        tokenSpec.put("parameters", tokenParams);
        cardMethod.put("tokenizationSpecification", tokenSpec);

        req.put("allowedPaymentMethods", new JSONArray().put(cardMethod));

        // Transaction info
        JSONObject transactionInfo = new JSONObject();
        transactionInfo.put("totalPrice", price);
        transactionInfo.put("totalPriceStatus", "FINAL");
        transactionInfo.put("currencyCode", "USD");
        transactionInfo.put("countryCode", "US");
        req.put("transactionInfo", transactionInfo);

        // Merchant info
        JSONObject merchantInfo = new JSONObject();
        merchantInfo.put("merchantName", MERCHANT_NAME);
        req.put("merchantInfo", merchantInfo);

        return req;
    }
}
