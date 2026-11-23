package com.example.promofinder.models;

import java.io.Serializable;

public class Category implements Serializable {
    private String id;
    private String name;
    private int iconResId;
    private boolean selected;

    public Category() {}

    public Category(String id, String name, int iconResId, boolean selected) {
        this.id = id;
        this.name = name;
        this.iconResId = iconResId;
        this.selected = selected;
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public int getIconResId() { return iconResId; }
    public void setIconResId(int iconResId) { this.iconResId = iconResId; }

    public boolean isSelected() { return selected; }
    public void setSelected(boolean selected) { this.selected = selected; }
}
