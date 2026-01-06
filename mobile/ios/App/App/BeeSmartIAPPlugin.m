#import <Foundation/Foundation.h>
#import <Capacitor/Capacitor.h>

// Capacitor v5 plugin export bridge.
// This file is required so the Swift plugin is discoverable from JS as:
//   window.Capacitor.Plugins.BeeSmartIAP
//
// Methods must match the @objc methods implemented in BeeSmartIAPPlugin.swift.
CAP_PLUGIN(BeeSmartIAPPlugin, "BeeSmartIAP",
           CAP_PLUGIN_METHOD(purchase, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(restorePurchases, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(getOwnedProducts, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(getInstallId, CAPPluginReturnPromise);
)
