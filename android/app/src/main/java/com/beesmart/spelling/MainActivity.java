package com.beesmart.spelling;

import android.content.Intent;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {

    private GooglePayPlugin googlePayPlugin;

    @Override
    public void onStart() {
        registerPlugin(GooglePayPlugin.class);
        super.onStart();
        try {
            googlePayPlugin = (GooglePayPlugin) getBridge().getPlugin("GooglePayPlugin").getInstance();
        } catch (Exception e) {
            // Plugin not yet available — will be resolved on first use
        }
    }

    /**
     * Forward Android activity results to GooglePayPlugin so the Google Pay sheet
     * can return its token/result back to the Capacitor JS layer.
     */
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (googlePayPlugin != null) {
            googlePayPlugin.handleActivityResult(requestCode, resultCode, data);
        }
    }
}
