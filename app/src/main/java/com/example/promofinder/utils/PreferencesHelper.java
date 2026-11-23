package com.example.promofinder.utils;

import android.content.Context;
import android.content.SharedPreferences;

import com.example.promofinder.models.PriceAlert;
import com.example.promofinder.models.Product;
import com.example.promofinder.models.User;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.List;

public class PreferencesHelper {
    private static final String PREF_NAME = "promofinder_prefs";
    private static final String KEY_FAVORITES = "key_favorites";
    private static final String KEY_PRICE_ALERTS = "key_price_alerts";
    private static final String KEY_USER_PROFILE = "key_user_profile";

    private final SharedPreferences sharedPreferences;
    private final Gson gson;

    public PreferencesHelper(Context context) {
        this.sharedPreferences = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        this.gson = new Gson();
    }

    // FAVORITES
    public List<Product> getFavorites() {
        String json = sharedPreferences.getString(KEY_FAVORITES, null);
        if (json == null) {
            return new ArrayList<>();
        }
        Type type = new TypeToken<List<Product>>() {}.getType();
        List<Product> favorites = gson.fromJson(json, type);
        return favorites != null ? favorites : new ArrayList<>();
    }

    public boolean isFavorite(String productId) {
        List<Product> favorites = getFavorites();
        for (Product p : favorites) {
            if (p.getId().equals(productId)) {
                return true;
            }
        }
        return false;
    }

    public void addFavorite(Product product) {
        List<Product> favorites = getFavorites();
        for (Product p : favorites) {
            if (p.getId().equals(product.getId())) {
                return; // Já está nos favoritos
            }
        }
        favorites.add(0, product);
        saveFavorites(favorites);
    }

    public void removeFavorite(String productId) {
        List<Product> favorites = getFavorites();
        Product toRemove = null;
        for (Product p : favorites) {
            if (p.getId().equals(productId)) {
                toRemove = p;
                break;
            }
        }
        if (toRemove != null) {
            favorites.remove(toRemove);
            saveFavorites(favorites);
        }
    }

    private void saveFavorites(List<Product> favorites) {
        String json = gson.toJson(favorites);
        sharedPreferences.edit().putString(KEY_FAVORITES, json).apply();
    }

    // PRICE ALERTS
    public List<PriceAlert> getPriceAlerts() {
        String json = sharedPreferences.getString(KEY_PRICE_ALERTS, null);
        if (json == null) {
            return new ArrayList<>();
        }
        Type type = new TypeToken<List<PriceAlert>>() {}.getType();
        List<PriceAlert> alerts = gson.fromJson(json, type);
        return alerts != null ? alerts : new ArrayList<>();
    }

    public void savePriceAlert(PriceAlert alert) {
        List<PriceAlert> alerts = getPriceAlerts();
        // Se já existir alerta para este produto, atualiza
        int existingIndex = -1;
        for (int i = 0; i < alerts.size(); i++) {
            if (alerts.get(i).getProduct().getId().equals(alert.getProduct().getId())) {
                existingIndex = i;
                break;
            }
        }
        if (existingIndex != -1) {
            alerts.set(existingIndex, alert);
        } else {
            alerts.add(0, alert);
        }
        String json = gson.toJson(alerts);
        sharedPreferences.edit().putString(KEY_PRICE_ALERTS, json).apply();
    }

    public void removePriceAlert(String alertId) {
        List<PriceAlert> alerts = getPriceAlerts();
        PriceAlert toRemove = null;
        for (PriceAlert a : alerts) {
            if (a.getId().equals(alertId)) {
                toRemove = a;
                break;
            }
        }
        if (toRemove != null) {
            alerts.remove(toRemove);
            String json = gson.toJson(alerts);
            sharedPreferences.edit().putString(KEY_PRICE_ALERTS, json).apply();
        }
    }

    // USER PROFILE
    public User getUserProfile() {
        String json = sharedPreferences.getString(KEY_USER_PROFILE, null);
        if (json == null) {
            return new User("user_001", "Alex Silva", "alex.silva@promofinder.com");
        }
        return gson.fromJson(json, User.class);
    }

    public void saveUserProfile(User user) {
        String json = gson.toJson(user);
        sharedPreferences.edit().putString(KEY_USER_PROFILE, json).apply();
    }
}
