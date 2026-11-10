// GestãoPro — Models.kt
// Data classes Kotlin para serialização JSON com Gson (EX5/EX7)
package br.com.gestaopro.data.model

import com.google.gson.annotations.SerializedName

// ── Auth ──────────────────────────────────────────────────────────────────────

data class LoginRequest(
    val email: String,
    val password: String
)

data class RefreshRequest(
    @SerializedName("refresh_token") val refreshToken: String
)

data class AuthResponse(
    @SerializedName("access_token")  val accessToken: String,
    @SerializedName("refresh_token") val refreshToken: String,
    @SerializedName("token_type")    val tokenType: String
)

data class UserResponse(
    val id: Int,
    val name: String,
    val email: String,
    val role: String,
    @SerializedName("is_active") val isActive: Boolean,
    @SerializedName("created_at") val createdAt: String?
)

data class MessageResponse(val message: String)

// ── Paginação ─────────────────────────────────────────────────────────────────

data class PagedResponse<T>(
    val items: List<T>,
    val total: Int,
    val page: Int,
    val limit: Int,
    val pages: Int
)

// ── Produtos ──────────────────────────────────────────────────────────────────

data class ProductResponse(
    val id: Int,
    val name: String,
    val sku: String,
    val category: String?,
    @SerializedName("category_id") val categoryId: Int?,
    val price: Double,
    val cost: Double,
    @SerializedName("stock_qty") val stockQty: Int,
    val unit: String,
    val description: String?,
    @SerializedName("release_date") val releaseDate: String?,
    val status: String,
    @SerializedName("created_at") val createdAt: String?,
    @SerializedName("updated_at") val updatedAt: String?
)

data class ProductRequest(
    val name: String,
    val sku: String,
    val price: Double,
    val cost: Double? = null,
    @SerializedName("stock_qty") val stockQty: Int = 0,
    val unit: String = "un",
    @SerializedName("category_id") val categoryId: Int? = null,
    val description: String? = null,
    @SerializedName("release_date") val releaseDate: String? = null,
    val status: String = "active"
)

// ── Clientes ──────────────────────────────────────────────────────────────────

data class CustomerResponse(
    val id: Int,
    val name: String,
    @SerializedName("person_type") val personType: String,
    val email: String?,
    val phone: String?,
    val document: String?,
    @SerializedName("birth_date") val birthDate: String?,
    @SerializedName("credit_limit") val creditLimit: Double,
    val address: String?,
    val city: String?,
    val state: String?,
    @SerializedName("zip_code") val zipCode: String?,
    val status: String,
    @SerializedName("created_at") val createdAt: String?
)

data class CustomerRequest(
    val name: String,
    @SerializedName("person_type") val personType: String = "PF",
    val email: String? = null,
    val phone: String? = null,
    val document: String? = null,
    @SerializedName("birth_date") val birthDate: String? = null,
    @SerializedName("credit_limit") val creditLimit: Double = 0.0,
    val address: String? = null,
    val city: String? = null,
    val state: String? = null,
    @SerializedName("zip_code") val zipCode: String? = null,
    val status: String = "active"
)

// ── Fornecedores ──────────────────────────────────────────────────────────────

data class SupplierResponse(
    val id: Int,
    @SerializedName("company_name") val companyName: String,
    @SerializedName("trade_name") val tradeName: String?,
    val cnpj: String?,
    val email: String?,
    val phone: String?,
    val contact: String?,
    val address: String?,
    val city: String?,
    val state: String?,
    @SerializedName("zip_code") val zipCode: String?,
    val category: String?,
    @SerializedName("contract_date") val contractDate: String?,
    val status: String,
    @SerializedName("created_at") val createdAt: String?
)

data class SupplierRequest(
    @SerializedName("company_name") val companyName: String,
    @SerializedName("trade_name") val tradeName: String? = null,
    val cnpj: String? = null,
    val email: String? = null,
    val phone: String? = null,
    val contact: String? = null,
    val address: String? = null,
    val city: String? = null,
    val state: String? = null,
    @SerializedName("zip_code") val zipCode: String? = null,
    val category: String? = null,
    @SerializedName("contract_date") val contractDate: String? = null,
    val status: String = "active"
)

// ── Erros ─────────────────────────────────────────────────────────────────────

data class ErrorResponse(
    val detail: String?,
    val errors: List<FieldError>?
)

data class FieldError(
    val field: String,
    val code: String,
    val message: String
)
