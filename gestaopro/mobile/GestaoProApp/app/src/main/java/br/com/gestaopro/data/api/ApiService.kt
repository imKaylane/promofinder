// GestãoPro — ApiService.kt
// Interface Retrofit com todos os endpoints da API (EX5/EX7)
package br.com.gestaopro.data.api

import br.com.gestaopro.data.model.*
import retrofit2.Response
import retrofit2.http.*

interface ApiService {

    // ── Auth ────────────────────────────────────────────────────────────────

    @POST("api/v1/auth/login")
    suspend fun login(@Body request: LoginRequest): Response<AuthResponse>

    @POST("api/v1/auth/refresh")
    suspend fun refresh(@Body request: RefreshRequest): Response<AuthResponse>

    @POST("api/v1/auth/logout")
    suspend fun logout(@Body request: RefreshRequest): Response<MessageResponse>

    @GET("api/v1/auth/me")
    suspend fun getMe(): Response<UserResponse>

    // ── Produtos ────────────────────────────────────────────────────────────

    @GET("api/v1/products")
    suspend fun listProducts(
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 20,
        @Query("search") search: String? = null,
        @Query("status") status: String? = null
    ): Response<PagedResponse<ProductResponse>>

    @GET("api/v1/products/{id}")
    suspend fun getProduct(@Path("id") id: Int): Response<ProductResponse>

    @POST("api/v1/products")
    suspend fun createProduct(@Body product: ProductRequest): Response<ProductResponse>

    @PUT("api/v1/products/{id}")
    suspend fun updateProduct(@Path("id") id: Int, @Body product: ProductRequest): Response<ProductResponse>

    @DELETE("api/v1/products/{id}")
    suspend fun deleteProduct(@Path("id") id: Int): Response<Unit>

    // ── Clientes ────────────────────────────────────────────────────────────

    @GET("api/v1/customers")
    suspend fun listCustomers(
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 20,
        @Query("search") search: String? = null,
        @Query("status") status: String? = null
    ): Response<PagedResponse<CustomerResponse>>

    @GET("api/v1/customers/{id}")
    suspend fun getCustomer(@Path("id") id: Int): Response<CustomerResponse>

    @POST("api/v1/customers")
    suspend fun createCustomer(@Body customer: CustomerRequest): Response<CustomerResponse>

    @PUT("api/v1/customers/{id}")
    suspend fun updateCustomer(@Path("id") id: Int, @Body customer: CustomerRequest): Response<CustomerResponse>

    @DELETE("api/v1/customers/{id}")
    suspend fun deleteCustomer(@Path("id") id: Int): Response<Unit>

    // ── Fornecedores ────────────────────────────────────────────────────────

    @GET("api/v1/suppliers")
    suspend fun listSuppliers(
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 20,
        @Query("search") search: String? = null,
        @Query("status") status: String? = null
    ): Response<PagedResponse<SupplierResponse>>

    @GET("api/v1/suppliers/{id}")
    suspend fun getSupplier(@Path("id") id: Int): Response<SupplierResponse>

    @POST("api/v1/suppliers")
    suspend fun createSupplier(@Body supplier: SupplierRequest): Response<SupplierResponse>

    @PUT("api/v1/suppliers/{id}")
    suspend fun updateSupplier(@Path("id") id: Int, @Body supplier: SupplierRequest): Response<SupplierResponse>

    @PATCH("api/v1/suppliers/{id}")
    suspend fun patchSupplier(@Path("id") id: Int, @Body patch: Map<String, String>): Response<SupplierResponse>

    @DELETE("api/v1/suppliers/{id}")
    suspend fun deleteSupplier(@Path("id") id: Int): Response<Unit>
}
