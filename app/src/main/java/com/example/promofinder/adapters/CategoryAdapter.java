package com.example.promofinder.adapters;

import android.view.LayoutInflater;
import android.view.ViewGroup;

import androidx.annotation.NonNull;
import androidx.core.content.ContextCompat;
import androidx.recyclerview.widget.RecyclerView;

import com.example.promofinder.R;
import com.example.promofinder.databinding.ItemCategoryBinding;
import com.example.promofinder.models.Category;

import java.util.ArrayList;
import java.util.List;

public class CategoryAdapter extends RecyclerView.Adapter<CategoryAdapter.CategoryViewHolder> {

    public interface OnCategoryClickListener {
        void onCategoryClick(Category category);
    }

    private List<Category> categories;
    private final OnCategoryClickListener listener;

    public CategoryAdapter(List<Category> categories, OnCategoryClickListener listener) {
        this.categories = categories != null ? categories : new ArrayList<>();
        this.listener = listener;
    }

    public void setCategories(List<Category> categories) {
        this.categories = categories != null ? categories : new ArrayList<>();
        notifyDataSetChanged();
    }

    public void selectCategory(String categoryId) {
        for (Category c : categories) {
            c.setSelected(c.getId().equals(categoryId) || (categoryId == null && c.getId().equals("cat_all")));
        }
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public CategoryViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        ItemCategoryBinding binding = ItemCategoryBinding.inflate(
                LayoutInflater.from(parent.getContext()), parent, false);
        return new CategoryViewHolder(binding);
    }

    @Override
    public void onBindViewHolder(@NonNull CategoryViewHolder holder, int position) {
        holder.bind(categories.get(position));
    }

    @Override
    public int getItemCount() {
        return categories.size();
    }

    class CategoryViewHolder extends RecyclerView.ViewHolder {
        private final ItemCategoryBinding binding;

        public CategoryViewHolder(@NonNull ItemCategoryBinding binding) {
            super(binding.getRoot());
            this.binding = binding;
        }

        public void bind(Category category) {
            binding.txtCategoryName.setText(category.getName());
            if (category.getIconResId() != 0) {
                binding.imgCategoryIcon.setImageResource(category.getIconResId());
            }

            if (category.isSelected()) {
                binding.layoutCategoryChip.setBackgroundResource(R.drawable.bg_button_green);
                binding.txtCategoryName.setTextColor(ContextCompat.getColor(itemView.getContext(), R.color.black));
                binding.imgCategoryIcon.setColorFilter(ContextCompat.getColor(itemView.getContext(), R.color.black));
            } else {
                binding.layoutCategoryChip.setBackgroundResource(R.drawable.bg_chip);
                binding.txtCategoryName.setTextColor(ContextCompat.getColor(itemView.getContext(), R.color.text_primary));
                binding.imgCategoryIcon.setColorFilter(ContextCompat.getColor(itemView.getContext(), R.color.text_primary));
            }

            itemView.setOnClickListener(v -> {
                selectCategory(category.getId());
                if (listener != null) {
                    listener.onCategoryClick(category);
                }
            });
        }
    }
}
