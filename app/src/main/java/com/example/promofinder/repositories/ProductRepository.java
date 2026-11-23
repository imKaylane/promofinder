package com.example.promofinder.repositories;

import com.example.promofinder.api.ApiClient;
import com.example.promofinder.api.BackendApi;
import com.example.promofinder.api.ProductResponse;
import com.example.promofinder.models.Product;
import com.example.promofinder.utils.DummyData;

import java.util.ArrayList;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class ProductRepository {

    public interface RepositoryCallback<T> {
        void onSuccess(T result);
        void onError(String errorMessage);
    }

    private final BackendApi backendApi;
    private boolean useLiveApi = true;

    public ProductRepository() {
        this.backendApi = ApiClient.getBackendClient().create(BackendApi.class);
    }

    public void setUseLiveApi(boolean useLiveApi) {
        this.useLiveApi = useLiveApi;
    }

    public void searchProducts(String query, String categoryFilter, double minPrice, double maxPrice,
                               String sortBy, RepositoryCallback<List<Product>> callback) {
        if (!useLiveApi) {
            List<Product> all = DummyData.getDummyProducts();
            List<Product> filtered = new ArrayList<>();
            for (Product product : all) {
                boolean matchesQuery = query == null || query.trim().isEmpty()
                        || product.getTitle().toLowerCase().contains(query.toLowerCase())
                        || product.getCategory().toLowerCase().contains(query.toLowerCase());
                boolean matchesCategory = categoryFilter == null || categoryFilter.equals("Todas")
                        || product.getCategory().equalsIgnoreCase(categoryFilter);
                boolean matchesMinPrice = minPrice <= 0 || product.getCurrentPrice() >= minPrice;
                boolean matchesMaxPrice = maxPrice <= 0 || product.getCurrentPrice() <= maxPrice;
                if (matchesQuery && matchesCategory && matchesMinPrice && matchesMaxPrice) filtered.add(product);
            }
            sortProducts(filtered, sortBy);
            callback.onSuccess(filtered);
            return;
        }

        if (query == null || query.trim().length() < 2) {
            callback.onSuccess(new ArrayList<>());
            return;
        }

        backendApi.searchLiveProducts(query.trim(), minPrice > 0 ? minPrice : null,
                maxPrice > 0 ? maxPrice : null, mapSort(sortBy), 0, 30)
                .enqueue(new Callback<ProductResponse>() {
                    @Override
                    public void onResponse(Call<ProductResponse> call, Response<ProductResponse> response) {
                        if (!response.isSuccessful() || response.body() == null) {
                            callback.onError("Falha na resposta do backend PromoFinder (HTTP " + response.code() + ").");
                            return;
                        }

                        List<Product> converted = new ArrayList<>();
                        List<ProductResponse.MlItem> items = response.body().getResults();
                        if (items != null) {
                            for (ProductResponse.MlItem item : items) {
                                if (item == null || item.getId() == null || item.getTitle() == null) continue;
                                double currentPrice = item.getPrice();
                                double previousPrice = item.getOriginalPrice() > currentPrice
                                        ? item.getOriginalPrice() : currentPrice;
                                Product product = new Product(
                                        item.getId(), item.getTitle(),
                                        "Produto disponível no Mercado Livre. Confira as condições e o frete.",
                                        item.getThumbnail() == null ? "" : item.getThumbnail().replace("http://", "https://"),
                                        currentPrice, previousPrice, "Geral", "Mercado Livre",
                                        item.getPermalink(), "Hoje"
                                );
                                converted.add(product);
                            }
                        }
                        sortProducts(converted, sortBy);
                        callback.onSuccess(converted);
                    }

                    @Override
                    public void onFailure(Call<ProductResponse> call, Throwable error) {
                        callback.onError("Não foi possível conectar ao backend PromoFinder: " + error.getMessage());
                    }
                });
    }

    private String mapSort(String sortBy) {
        if ("Menor preço".equalsIgnoreCase(sortBy)) return "price_asc";
        if ("Maior preço".equalsIgnoreCase(sortBy)) return "price_desc";
        return "relevance";
    }

    private void sortProducts(List<Product> products, String sortBy) {
        if ("Menor preço".equalsIgnoreCase(sortBy)) {
            products.sort((a, b) -> Double.compare(a.getCurrentPrice(), b.getCurrentPrice()));
        } else if ("Maior preço".equalsIgnoreCase(sortBy)) {
            products.sort((a, b) -> Double.compare(b.getCurrentPrice(), a.getCurrentPrice()));
        } else if ("Maior desconto".equalsIgnoreCase(sortBy)) {
            products.sort((a, b) -> Integer.compare(b.getDiscountPercentage(), a.getDiscountPercentage()));
        }
    }

    public void getFeaturedDeals(RepositoryCallback<List<Product>> callback) {
        searchProducts("placa de video", null, 0, 0, "Relevância", new RepositoryCallback<List<Product>>() {
            @Override
            public void onSuccess(List<Product> products) {
                List<Product> featured = new ArrayList<>();
                for (Product product : products) {
                    if (product.getDiscountPercentage() >= 15) featured.add(product);
                }
                callback.onSuccess(featured);
            }

            @Override
            public void onError(String errorMessage) { callback.onError(errorMessage); }
        });
    }

    public void getTopPriceDrops(RepositoryCallback<List<Product>> callback) {
        searchProducts("processador", null, 0, 0, "Maior desconto", new RepositoryCallback<List<Product>>() {
            @Override
            public void onSuccess(List<Product> products) { callback.onSuccess(products); }
            @Override
            public void onError(String errorMessage) { callback.onError(errorMessage); }
        });
    }
}
