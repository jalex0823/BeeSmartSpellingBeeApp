package com.beesmart.spellingbee;

import android.app.Activity;
import android.content.Intent;
import android.util.Log;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
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
 * JS usage:
 *   const plugin = Capacitor.Plugins.GooglePayPlugin;
 *   const { available } = await plugin.isReadyToPay();
 *   const result = await plugin.startPayment({ productId: 'premium_monthly', price: '3.99' });
 *
 * TODO (before Play Store production submission):
 *   1. Replace GATEWAY and GATEWAY_MERCHANT_ID with real gateway values (e.g. "stripe" / acct_XXX)
 *   2. Switch WALLET_ENVIRONMENT to WalletConstants.ENVIRONMENT_PRODUCTION
 *      only after Google Pay Business Profile is approved at pay.google.com/business/console
 */
@CapacitorPlugin(name = "GooglePayPlugin")
public class GooglePayPlugin extends Plugin {

    private static final String TAG = "GooglePayPlugin";
    private static final int LOAD_PAYMENT_DATA_REQUEST_CODE = 991;

    // TODO: replace with real gateway values before production
    private static final String GATEWAY = "example";
    private static final String GATEWAY_MERCHANT_ID = "exampleMerchantId";
    private static final String MERCHANT_NAME = "BeeSmart Spelling";

    // TODO: switch to ENVIRONMENT_PRODUCTION after Google Pay Business Profile approval
    private static final int WALLET_ENVIRONMENT = WalletConstants.ENVIRONMENT_TEST;

    private PaymentsClient paymentsClient;
    private PluginCall pendingPaymentCall;

    @Override
    public void load() {
        paymentsClient = Wallet.getPaymentsClient(
            getActivity(),
            new Wallet.WalletOptions.Builder()
                .setEnvironment(WALLET_ENVIRONMENT)
                .build()
        );
    }

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

    @PluginMethod
    public void startPayment(PluginCall call) {
        String price = call.getString("price", "3.99");
        try {
            PaymentDataRequest request = PaymentDataRequest.fromJson(
                buildPaymentDataRequest(price).toString()
            );
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

    public void handleActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode != LOAD_PAYMENT_DATA_REQUEST_CODE) return;
        PluginCall savedCall = pendingPaymentCall;
        pendingPaymentCall = null;
        if (savedCall == null) return;

        switch (resultCode) {
            case Activity.RESULT_OK: {
                PaymentData paymentData = PaymentData.getFromIntent(data);
                if (paymentData == null) {
                    savedCall.reject("PaymentData is null");
                    return;
                }
                try {
                    String paymentJson = paymentData.toJson();
                    JSONObject paymentObj = new JSONObject(paymentJson);
                    String token = paymentObj
                        .getJSONObject("paymentMethodData")
                        .getJSONObject("tokenizationData")
                        .getString("token");
                    String email = "";
                    try { email = paymentObj.getString("email"); } catch (Exception ignored) {}
                    JSObject result = new JSObject();
                    result.put("token", token);
                    result.put("email", email);
                    result.put("rawJson", paymentJson);
                    savedCall.resolve(result);
                } catch (Exception e) {
                    savedCall.reject("Failed to parse payment result: " + e.getMessage(), e);
                }
                break;
            }
            case Activity.RESULT_CANCELED: {
                JSObject cancelled = new JSObject();
                cancelled.put("cancelled", true);
                savedCall.resolve(cancelled);
                break;
            }
            case AutoResolveHelper.RESULT_ERROR:
                savedCall.reject("Google Pay returned an error. Check your merchant configuration.");
                break;
            default:
                savedCall.reject("Unexpected result code: " + resultCode);
                break;
        }
    }

    private JSONObject buildIsReadyToPayRequest() throws Exception {
        JSONObject req = new JSONObject();
        req.put("apiVersion", 2);
        req.put("apiVersionMinor", 0);
        JSONObject card = new JSONObject();
        card.put("type", "CARD");
        JSONObject params = new JSONObject();
        params.put("allowedAuthMethods", new JSONArray().put("PAN_ONLY").put("CRYPTOGRAM_3DS"));
        params.put("allowedCardNetworks", new JSONArray()
            .put("VISA").put("MASTERCARD").put("AMEX").put("DISCOVER"));
        card.put("parameters", params);
        req.put("allowedPaymentMethods", new JSONArray().put(card));
        return req;
    }

    private JSONObject buildPaymentDataRequest(String price) throws Exception {
        JSONObject req = new JSONObject();
        req.put("apiVersion", 2);
        req.put("apiVersionMinor", 0);

        JSONObject cardMethod = new JSONObject();
        cardMethod.put("type", "CARD");
        JSONObject cardParams = new JSONObject();
        cardParams.put("allowedAuthMethods", new JSONArray().put("PAN_ONLY").put("CRYPTOGRAM_3DS"));
        cardParams.put("allowedCardNetworks", new JSONArray()
            .put("VISA").put("MASTERCARD").put("AMEX").put("DISCOVER"));
        cardMethod.put("parameters", cardParams);

        JSONObject tokenSpec = new JSONObject();
        tokenSpec.put("type", "PAYMENT_GATEWAY");
        JSONObject tokenParams = new JSONObject();
        tokenParams.put("gateway", GATEWAY);
        tokenParams.put("gatewayMerchantId", GATEWAY_MERCHANT_ID);
        tokenSpec.put("parameters", tokenParams);
        cardMethod.put("tokenizationSpecification", tokenSpec);

        req.put("allowedPaymentMethods", new JSONArray().put(cardMethod));

        JSONObject transactionInfo = new JSONObject();
        transactionInfo.put("totalPrice", price);
        transactionInfo.put("totalPriceStatus", "FINAL");
        transactionInfo.put("currencyCode", "USD");
        transactionInfo.put("countryCode", "US");
        req.put("transactionInfo", transactionInfo);

        JSONObject merchantInfo = new JSONObject();
        merchantInfo.put("merchantName", MERCHANT_NAME);
        req.put("merchantInfo", merchantInfo);

        return req;
    }
}
