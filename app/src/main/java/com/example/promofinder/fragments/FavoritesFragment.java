package com.example.promofinder.fragments;

import android.content.Intent;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;

import com.example.promofinder.activities.ProductDetailsActivity;
import com.example.promofinder.adapters.ProductAdapter;
import com.example.promofinder.databinding.FragmentFavoritesBinding;
import com.example.promofinder.models.Product;
import com.example.promofinder.utils.PreferencesHelper;

import java.util.List;

public class FavoritesFragment extends Fragment implements ProductAdapter.OnProductClickListener {

    private FragmentFavoritesBinding binding;
    private PreferencesHelper preferencesHelper;
    private ProductAdapter adapter;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container,
                             @Nullable Bundle savedInstanceState) {
        binding = FragmentFavoritesBinding.inflate(inflater, container, false);
        return binding.getRoot();
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        preferencesHelper = new PreferencesHelper(requireContext());
        setupRecyclerView();
    }

    @Override
    public void onResume() {
        super.onResume();
        loadFavorites();
    }

    private void setupRecyclerView() {
        binding.rvFavorites.setLayoutManager(new LinearLayoutManager(getContext()));
        adapter = new ProductAdapter(null, this);
        binding.rvFavorites.setAdapter(adapter);
    }

    private void loadFavorites() {
        List<Product> favorites = preferencesHelper.getFavorites();
        if (favorites.isEmpty()) {
            binding.rvFavorites.setVisibility(View.GONE);
            binding.layoutEmptyFavorites.setVisibility(View.VISIBLE);
        } else {
            binding.rvFavorites.setVisibility(View.VISIBLE);
            binding.layoutEmptyFavorites.setVisibility(View.GONE);
            adapter.setProducts(favorites);
        }
    }

    @Override
    public void onProductClick(Product product) {
        Intent intent = new Intent(getContext(), ProductDetailsActivity.class);
        intent.putExtra("product", product);
        startActivity(intent);
    }

    @Override
    public void onFavoriteClick(Product product, boolean isFavoriteNow) {
        loadFavorites(); // Refresh favorites list
    }

    @Override
    public void onViewOfferClick(Product product) {
        if (product.getProductUrl() != null && !product.getProductUrl().isEmpty()) {
            Intent intent = new Intent(Intent.ACTION_VIEW, android.net.Uri.parse(product.getProductUrl()));
            startActivity(intent);
        }
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();
        binding = null;
    }
}
