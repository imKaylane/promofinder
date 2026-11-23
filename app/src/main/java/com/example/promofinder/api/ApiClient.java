package com.example.promofinder.api;

import com.example.promofinder.BuildConfig;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

public final class ApiClient {
    private static Retrofit backendRetrofit;

    private ApiClient() {}

    public static Retrofit getBackendClient() {
        if (backendRetrofit == null) {
            backendRetrofit = new Retrofit.Builder()
                    .baseUrl(BuildConfig.BACKEND_BASE_URL)
                    .addConverterFactory(GsonConverterFactory.create())
                    .build();
        }
        return backendRetrofit;
    }
}
