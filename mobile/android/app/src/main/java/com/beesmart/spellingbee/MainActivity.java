package com.beesmart.spellingbee;

import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {

	private GooglePayPlugin googlePayPlugin;

	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		registerPlugin(BeeSmartIAPPlugin.class);
		registerPlugin(GooglePayPlugin.class);
		try {
			googlePayPlugin = (GooglePayPlugin) getBridge().getPlugin("GooglePayPlugin").getInstance();
		} catch (Exception e) {
			// Plugin resolves on first use
		}

		// Configure WebView for smooth scrolling and proper touch handling
		try {
			WebView webView = getBridge().getWebView();
			
			// Set background to app theme color to prevent white flash on page transitions
			webView.setBackgroundColor(Color.parseColor("#FFF9E6"));
			
			// CRITICAL: Enable scrolling in WebView
			WebSettings settings = webView.getSettings();
			
			// Enable JavaScript (required for touch events)
			settings.setJavaScriptEnabled(true);
			
			// Enable DOM storage for localStorage/sessionStorage
			settings.setDomStorageEnabled(true);
			
			// Enable database storage
			settings.setDatabaseEnabled(true);
			
			// Set viewport to allow proper scaling
			settings.setUseWideViewPort(true);
			settings.setLoadWithOverviewMode(true);
			
			// Enable smooth scrolling
			webView.setVerticalScrollBarEnabled(true);
			webView.setHorizontalScrollBarEnabled(false);
			webView.setScrollbarFadingEnabled(true);
			
			// Enable touch events to pass through properly
			webView.requestFocusFromTouch();
			
			// Set overscroll mode to enable bounce effect on Android 4.0+
			webView.setOverScrollMode(WebView.OVER_SCROLL_IF_CONTENT_SCROLLS);
			
			// Enable hardware acceleration for smooth scrolling
			webView.setLayerType(WebView.LAYER_TYPE_HARDWARE, null);
			
		} catch (Exception e) {
			// Bridge may not be ready yet; ignore
			e.printStackTrace();
		}
	}

	@Override
	protected void onActivityResult(int requestCode, int resultCode, Intent data) {
		super.onActivityResult(requestCode, resultCode, data);
		if (googlePayPlugin != null) {
			googlePayPlugin.handleActivityResult(requestCode, resultCode, data);
		}
	}
}
