package com.example.promofinder.api;

import com.google.gson.annotations.SerializedName;
import java.util.List;

public class ProductResponse {
    @SerializedName("site_id")
    private String siteId;

    @SerializedName("query")
    private String query;

    @SerializedName("results")
    private List<MlItem> results;

    public String getSiteId() { return siteId; }
    public String getQuery() { return query; }
    public List<MlItem> getResults() { return results; }

    public static class MlItem {
        @SerializedName("id")
        private String id;

        @SerializedName("title")
        private String title;

        @SerializedName("price")
        private double price;

        @SerializedName("original_price")
        private double originalPrice;

        @SerializedName("thumbnail")
        private String thumbnail;

        @SerializedName("permalink")
        private String permalink;

        @SerializedName("category_id")
        private String categoryId;

        public String getId() { return id; }
        public String getTitle() { return title; }
        public double getPrice() { return price; }
        public double getOriginalPrice() { return originalPrice; }
        public String getThumbnail() { return thumbnail; }
        public String getPermalink() { return permalink; }
        public String getCategoryId() { return categoryId; }
    }
}
