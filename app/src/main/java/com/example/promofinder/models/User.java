package com.example.promofinder.models;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

public class User implements Serializable {
    private String id;
    private String name;
    private String email;
    private boolean priceAlertsEnabled;
    private boolean promoNotificationsEnabled;
    private List<String> favoriteCategories;

    public User() {
        this.favoriteCategories = new ArrayList<>();
        this.priceAlertsEnabled = true;
        this.promoNotificationsEnabled = true;
    }

    public User(String id, String name, String email) {
        this();
        this.id = id;
        this.name = name;
        this.email = email;
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public boolean isPriceAlertsEnabled() { return priceAlertsEnabled; }
    public void setPriceAlertsEnabled(boolean priceAlertsEnabled) { this.priceAlertsEnabled = priceAlertsEnabled; }

    public boolean isPromoNotificationsEnabled() { return promoNotificationsEnabled; }
    public void setPromoNotificationsEnabled(boolean promoNotificationsEnabled) { this.promoNotificationsEnabled = promoNotificationsEnabled; }

    public List<String> getFavoriteCategories() { return favoriteCategories; }
    public void setFavoriteCategories(List<String> favoriteCategories) { this.favoriteCategories = favoriteCategories; }
}
