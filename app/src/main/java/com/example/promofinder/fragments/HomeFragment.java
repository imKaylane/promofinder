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

import com.example.promofinder.MainActivity;
import com.example.promofinder.activities.ProductDetailsActivity;
import com.example.promofinder.adapters.CategoryAdapter;
import com.example.promofinder.adapters.ProductAdapter;
import com.example.promofinder.databinding.FragmentHomeBinding;
import com.example.promofinder.models.Category;
import com.example.promofinder.models.Product;
import com.example.promofinder.repositories.ProductRepository;
import com.example.promofinder.utils.DummyData;

import java.util.List;

public class HomeFragment extends Fragment implements ProductAdapter.OnProductClickListener {

    private FragmentHomeBinding binding;
    private ProductRepository repository;
    private ProductAdapter featuredAdapter;
    private ProductAdapter dropsAdapter;
    private CategoryAdapter categoryAdapter;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container,
                             @Nullable Bundle savedInstanceState) {
        binding = FragmentHomeBinding.inflate(inflater, container, false);
        return binding.getRoot();
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        repository = new ProductRepository();

        setupCategories();
        setupRecyclerViews();
        setupListeners();
        loadData();
    }

    private void setupCategories() {
        categoryAdapter = new CategoryAdapter(DummyData.getCategories(), category -> {
            if (getActivity() instanceof MainActivity) {
                String catName = category.getName().equals("Todas") ? "" : category.getName();
                ((MainActivity) getActivity()).navigateToSearch(catName);
            }
        });
        binding.rvCategories.setAdapter(categoryAdapter);
    }

    private void setupRecyclerViews() {
        binding.rvFeaturedDeals.setLayoutManager(new LinearLayoutManager(getContext()));
        featuredAdapter = new ProductAdapter(null, this);
        binding.rvFeaturedDeals.setAdapter(featuredAdapter);

        binding.rvTopPriceDrops.setLayoutManager(new LinearLayoutManager(getContext()));
        dropsAdapter = new ProductAdapter(null, this);
        binding.rvTopPriceDrops.setAdapter(dropsAdapter);
    }

    private void setupListeners() {
        binding.searchBarContainer.setOnClickListener(v -> {
            if (getActivity() instanceof MainActivity) {
                ((MainActivity) getActivity()).navigateToSearch("");
            }
        });

        binding.btnViewAllFeatured.setOnClickListener(v -> {
            if (getActivity() instanceof MainActivity) {
                ((MainActivity) getActivity()).navigateToSearch("");
            }
        });

        binding.btnViewAllDrops.setOnClickListener(v -> {
            if (getActivity() instanceof MainActivity) {
                ((MainActivity) getActivity()).navigateToSearch("");
            }
        });
    }

    private void loadData() {
        repository.getFeaturedDeals(new ProductRepository.RepositoryCallback<List<Product>>() {
            @Override
            public void onSuccess(List<Product> result) {
                featuredAdapter.setProducts(result);
            }

            @Override
            public void onError(String errorMessage) {}
        });

        repository.getTopPriceDrops(new ProductRepository.RepositoryCallback<List<Product>>() {
            @Override
            public void onSuccess(List<Product> result) {
                dropsAdapter.setProducts(result);
            }

            @Override
            public void onError(String errorMessage) {}
        });
    }

    @Override
    public void onProductClick(Product product) {
        Intent intent = new Intent(getContext(), ProductDetailsActivity.class);
        intent.putExtra("product", product);
        startActivity(intent);
    }

    @Override
    public void onFavoriteClick(Product product, boolean isFavoriteNow) {}

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
