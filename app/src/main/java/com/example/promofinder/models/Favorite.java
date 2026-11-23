package com.example.promofinder.models;

import java.io.Serializable;

public class Favorite implements Serializable {
    private String id;
    private Product product;
    private String addedAt;

    public Favorite() {}

    public Favorite(String id, Product product, String addedAt) {
        this.id = id;
        this.product = product;
        this.addedAt = addedAt;
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public Product getProduct() { return product; }
    public void setProduct(Product product) { this.product = product; }

    public String getAddedAt() { return addedAt; }
    public void setAddedAt(String addedAt) { this.addedAt = addedAt; }
}
