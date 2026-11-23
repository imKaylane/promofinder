package com.example.promofinder.models;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

public class Product implements Serializable {
    private String id;
    private String title;
    private String description;
    private String imageUrl;
    private double currentPrice;
    private double previousPrice;
    private int discountPercentage;
    private String category;
    private String marketplace;
    private String productUrl;
    private String lastUpdated;
    private List<PriceHistoryPoint> priceHistory;

    public Product() {
        this.priceHistory = new ArrayList<>();
    }

    public Product(String id, String title, String description, String imageUrl,
                   double currentPrice, double previousPrice, String category,
                   String marketplace, String productUrl, String lastUpdated) {
        this.id = id;
        this.title = title;
        this.description = description;
        this.imageUrl = imageUrl;
        this.currentPrice = currentPrice;
        this.previousPrice = previousPrice;
        this.category = category;
        this.marketplace = marketplace;
        this.productUrl = productUrl;
        this.lastUpdated = lastUpdated;
        this.priceHistory = new ArrayList<>();
        calculateDiscount();
    }

    public void calculateDiscount() {
        if (previousPrice > currentPrice && previousPrice > 0) {
            double discount = ((previousPrice - currentPrice) / previousPrice) * 100.0;
            this.discountPercentage = (int) Math.round(discount);
        } else {
            this.discountPercentage = 0;
        }
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public String getImageUrl() { return imageUrl; }
    public void setImageUrl(String imageUrl) { this.imageUrl = imageUrl; }

    public double getCurrentPrice() { return currentPrice; }
    public void setCurrentPrice(double currentPrice) {
        this.currentPrice = currentPrice;
        calculateDiscount();
    }

    public double getPreviousPrice() { return previousPrice; }
    public void setPreviousPrice(double previousPrice) {
        this.previousPrice = previousPrice;
        calculateDiscount();
    }

    public int getDiscountPercentage() { return discountPercentage; }
    public void setDiscountPercentage(int discountPercentage) { this.discountPercentage = discountPercentage; }

    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }

    public String getMarketplace() { return marketplace; }
    public void setMarketplace(String marketplace) { this.marketplace = marketplace; }

    public String getProductUrl() { return productUrl; }
    public void setProductUrl(String productUrl) { this.productUrl = productUrl; }

    public String getLastUpdated() { return lastUpdated; }
    public void setLastUpdated(String lastUpdated) { this.lastUpdated = lastUpdated; }

    public List<PriceHistoryPoint> getPriceHistory() { return priceHistory; }
    public void setPriceHistory(List<PriceHistoryPoint> priceHistory) { this.priceHistory = priceHistory; }
}
