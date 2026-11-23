package com.example.promofinder.api;

import retrofit2.Call;
import retrofit2.http.GET;
import retrofit2.http.Query;

/** Endpoints shared with the PromoFinder web backend (FastAPI /api/v1). */
public interface BackendApi {
    @GET("api/v1/products/search/live")
    Call<ProductResponse> searchLiveProducts(
            @Query("q") String query,
            @Query("min_price") Double minPrice,
            @Query("max_price") Double maxPrice,
            @Query("sort") String sort,
            @Query("offset") int offset,
            @Query("limit") int limit
    );
}
