
        // CRITICAL: Set auth state EARLY so tile-locking logic works correctly
        window.IS_AUTH = {{ _is_auth }};
        window.IS_PREMIUM = {{ _is_premium }};
        window.BILLING_MODE = '{{ _billing_mode }}';
        window.SUBSCRIPTION_SKU = '{{ _subscription_sku }}';
        window.SUBSCRIPTION_MONTHLY_USD = {{ _subscription_monthly }};
        console.log(' Auth state set:', window.IS_AUTH ? 'Authenticated' : 'Guest');
    