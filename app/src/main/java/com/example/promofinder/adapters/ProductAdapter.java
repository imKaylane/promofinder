package com.example.promofinder.adapters;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.bumptech.glide.Glide;
import com.example.promofinder.R;
import com.example.promofinder.databinding.ItemProductBinding;
import com.example.promofinder.models.Product;
import com.example.promofinder.utils.FormatUtils;
import com.example.promofinder.utils.PreferencesHelper;

import java.util.ArrayList;
import java.util.List;

public class ProductAdapter extends RecyclerView.Adapter<ProductAdapter.ProductViewHolder> {

    public interface OnProductClickListener {
        void onProductClick(Product product);
        void onFavoriteClick(Product product, boolean isFavoriteNow);
        void onViewOfferClick(Product product);
    }

    private List<Product> products;
    private final OnProductClickListener listener;
    private PreferencesHelper preferencesHelper;

    public ProductAdapter(List<Product> products, OnProductClickListener listener) {
        this.products = products != null ? products : new ArrayList<>();
        this.listener = listener;
    }

    public void setProducts(List<Product> newProducts) {
        this.products = newProducts != null ? newProducts : new ArrayList<>();
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public ProductViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        if (preferencesHelper == null) {
            preferencesHelper = new PreferencesHelper(parent.getContext());
        }
        ItemProductBinding binding = ItemProductBinding.inflate(
                LayoutInflater.from(parent.getContext()), parent, false);
        return new ProductViewHolder(binding);
    }

    @Override
    public void onBindViewHolder(@NonNull ProductViewHolder holder, int position) {
        holder.bind(products.get(position));
    }

    @Override
    public int getItemCount() {
        return products.size();
    }

    class ProductViewHolder extends RecyclerView.ViewHolder {
        private final ItemProductBinding binding;

        public ProductViewHolder(@NonNull ItemProductBinding binding) {
            super(binding.getRoot());
            this.binding = binding;
        }

        public void bind(Product product) {
            binding.txtTitle.setText(product.getTitle());
            binding.txtCurrentPrice.setText(FormatUtils.formatCurrency(product.getCurrentPrice()));
            binding.txtMarketplace.setText(product.getMarketplace());

            if (product.getPreviousPrice() > product.getCurrentPrice()) {
                binding.txtPreviousPrice.setVisibility(View.VISIBLE);
                binding.txtPreviousPrice.setText(FormatUtils.formatCurrency(product.getPreviousPrice()));
                binding.txtPreviousPrice.setPaintFlags(binding.txtPreviousPrice.getPaintFlags() | android.graphics.Paint.STRIKE_THRU_TEXT_FLAG);

                binding.txtDiscountBadge.setVisibility(View.VISIBLE);
                binding.txtDiscountBadge.setText(FormatUtils.formatDiscount(product.getDiscountPercentage()));
            } else {
                binding.txtPreviousPrice.setVisibility(View.GONE);
                binding.txtDiscountBadge.setVisibility(View.GONE);
            }

            // Image
            Glide.with(itemView.getContext())
                    .load(product.getImageUrl())
                    .placeholder(R.drawable.ic_launcher_background)
                    .error(R.drawable.ic_launcher_background)
                    .into(binding.imgProduct);

            // Favorite state
            boolean isFav = preferencesHelper.isFavorite(product.getId());
            binding.btnFavorite.setImageResource(isFav ? R.drawable.ic_favorite_filled : R.drawable.ic_favorite);

            binding.btnFavorite.setOnClickListener(v -> {
                boolean newFavState = !preferencesHelper.isFavorite(product.getId());
                if (newFavState) {
                    preferencesHelper.addFavorite(product);
                } else {
                    preferencesHelper.removeFavorite(product.getId());
                }
                binding.btnFavorite.setImageResource(newFavState ? R.drawable.ic_favorite_filled : R.drawable.ic_favorite);
                if (listener != null) {
                    listener.onFavoriteClick(product, newFavState);
                }
            });

            itemView.setOnClickListener(v -> {
                if (listener != null) {
                    listener.onProductClick(product);
                }
            });

            binding.btnViewOffer.setOnClickListener(v -> {
                if (listener != null) {
                    listener.onViewOfferClick(product);
                }
            });
        }
    }
}
