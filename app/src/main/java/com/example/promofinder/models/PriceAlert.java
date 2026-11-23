package com.example.promofinder.models;

import java.io.Serializable;

public class PriceAlert implements Serializable {
    private String id;
    private Product product;
    private double targetPrice;
    private boolean active;
    private String createdAt;

    public PriceAlert() {}

    public PriceAlert(String id, Product product, double targetPrice, boolean active, String createdAt) {
        this.id = id;
        this.product = product;
        this.targetPrice = targetPrice;
        this.active = active;
        this.createdAt = createdAt;
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public Product getProduct() { return product; }
    public void setProduct(Product product) { this.product = product; }

    public double getTargetPrice() { return targetPrice; }
    public void setTargetPrice(double targetPrice) { this.targetPrice = targetPrice; }

    public boolean isActive() { return active; }
    public void setActive(boolean active) { this.active = active; }

    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
}
