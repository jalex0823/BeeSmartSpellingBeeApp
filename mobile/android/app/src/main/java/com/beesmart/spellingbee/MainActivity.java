package com.beesmart.spellingbee;

import android.graphics.Color;
import android.os.Bundle;
import android.webkit.WebView;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		registerPlugin(BeeSmartIAPPlugin.class);

		// Set WebView background to app theme color to prevent white flash on page transitions
		try {
			WebView webView = getBridge().getWebView();
			webView.setBackgroundColor(Color.parseColor("#FFF9E6"));
		} catch (Exception e) {
			// Bridge may not be ready yet; ignore
		}
	}
}
