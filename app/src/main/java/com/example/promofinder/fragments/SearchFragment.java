package com.example.promofinder.fragments;

import android.content.Intent;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;

import com.example.promofinder.activities.ProductDetailsActivity;
import com.example.promofinder.adapters.ProductAdapter;
import com.example.promofinder.databinding.FragmentSearchBinding;
import com.example.promofinder.models.Product;
import com.example.promofinder.repositories.ProductRepository;

import java.util.List;

public class SearchFragment extends Fragment implements ProductAdapter.OnProductClickListener {

    private FragmentSearchBinding binding;
    private ProductRepository repository;
    private ProductAdapter adapter;
    private String initialQuery = "";
    private boolean isSpinnerInitialized = false;

    public static SearchFragment newInstance(String query) {
        SearchFragment fragment = new SearchFragment();
        Bundle args = new Bundle();
        args.putString("query", query);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            initialQuery = getArguments().getString("query", "");
        }
    }

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container,
                             @Nullable Bundle savedInstanceState) {
        binding = FragmentSearchBinding.inflate(inflater, container, false);
        return binding.getRoot();
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        repository = new ProductRepository();

        if (!initialQuery.isEmpty()) {
            binding.etSearchQuery.setText(initialQuery);
        }

        setupSpinner();
        setupRecyclerView();
        setupListeners();
        performSearch();
    }

    private void setupSpinner() {
        String[] sortOptions = new String[]{"Relevância", "Menor preço", "Maior desconto"};
        ArrayAdapter<String> spinnerAdapter = new ArrayAdapter<>(requireContext(),
                android.R.layout.simple_spinner_item, sortOptions);
        spinnerAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        binding.spinnerSort.setAdapter(spinnerAdapter);

        binding.spinnerSort.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                if (!isSpinnerInitialized) {
                    isSpinnerInitialized = true;
                    return;
                }
                performSearch();
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {}
        });
    }

    private void setupRecyclerView() {
        binding.rvSearchResults.setLayoutManager(new LinearLayoutManager(getContext()));
        adapter = new ProductAdapter(null, this);
        binding.rvSearchResults.setAdapter(adapter);
    }

    private void setupListeners() {
        binding.btnDoSearch.setOnClickListener(v -> performSearch());

        binding.etSearchQuery.setOnEditorActionListener((v, actionId, event) -> {
            performSearch();
            return true;
        });

        binding.btnToggleFilter.setOnClickListener(v -> {
            if (binding.layoutPriceFilter.getVisibility() == View.VISIBLE) {
                binding.layoutPriceFilter.setVisibility(View.GONE);
            } else {
                binding.layoutPriceFilter.setVisibility(View.VISIBLE);
            }
        });

        binding.btnApplyPriceFilter.setOnClickListener(v -> performSearch());
    }

    private void performSearch() {
        if (binding == null) return;

        String query = binding.etSearchQuery.getText().toString().trim();
        String sortBy = binding.spinnerSort.getSelectedItem() != null ?
                binding.spinnerSort.getSelectedItem().toString() : "Relevância";

        double minPrice = 0;
        double maxPrice = 0;

        try {
            String minStr = binding.etMinPrice.getText().toString();
            if (!minStr.isEmpty()) minPrice = Double.parseDouble(minStr);
        } catch (NumberFormatException ignored) {}

        try {
            String maxStr = binding.etMaxPrice.getText().toString();
            if (!maxStr.isEmpty()) maxPrice = Double.parseDouble(maxStr);
        } catch (NumberFormatException ignored) {}

        repository.searchProducts(query, null, minPrice, maxPrice, sortBy,
                new ProductRepository.RepositoryCallback<List<Product>>() {
                    @Override
                    public void onSuccess(List<Product> result) {
                        if (binding == null || !isAdded()) return;

                        if (result == null || result.isEmpty()) {
                            binding.rvSearchResults.setVisibility(View.GONE);
                            binding.txtEmptyResults.setVisibility(View.VISIBLE);
                        } else {
                            binding.rvSearchResults.setVisibility(View.VISIBLE);
                            binding.txtEmptyResults.setVisibility(View.GONE);
                            adapter.setProducts(result);
                        }
                    }

                    @Override
                    public void onError(String errorMessage) {
                        if (binding == null || !isAdded()) return;

                        binding.rvSearchResults.setVisibility(View.GONE);
                        binding.txtEmptyResults.setVisibility(View.VISIBLE);
                        binding.txtEmptyResults.setText("Erro: " + errorMessage);
                        Toast.makeText(requireContext(), errorMessage, Toast.LENGTH_LONG).show();
                    }
                });
    }

    @Override
    public void onProductClick(Product product) {
        if (getContext() == null) return;
        Intent intent = new Intent(getContext(), ProductDetailsActivity.class);
        intent.putExtra("product", product);
        startActivity(intent);
    }

    @Override
    public void onFavoriteClick(Product product, boolean isFavoriteNow) {}

    @Override
    public void onViewOfferClick(Product product) {
        if (getContext() != null && product.getProductUrl() != null && !product.getProductUrl().isEmpty()) {
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