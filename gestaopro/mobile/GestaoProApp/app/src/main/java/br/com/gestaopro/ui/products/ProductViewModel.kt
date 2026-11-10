// GestãoPro — ProductViewModel.kt
// ViewModel para listagem e CRUD de produtos (EX7)
package br.com.gestaopro.ui.products

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import br.com.gestaopro.data.api.RetrofitClient
import br.com.gestaopro.data.model.PagedResponse
import br.com.gestaopro.data.model.ProductResponse
import kotlinx.coroutines.launch

sealed class ProductsState {
    object Loading : ProductsState()
    data class Success(val data: PagedResponse<ProductResponse>) : ProductsState()
    data class Error(val message: String) : ProductsState()
}

class ProductViewModel : ViewModel() {

    private val _state = MutableLiveData<ProductsState>()
    val state: LiveData<ProductsState> = _state

    private var _currentPage = 1
    private var _search: String? = null

    fun loadProducts(page: Int = 1, search: String? = null) {
        _currentPage = page
        _search = search
        _state.value = ProductsState.Loading

        viewModelScope.launch {
            try {
                val response = RetrofitClient.instance.listProducts(
                    page = page,
                    search = search
                )
                if (response.isSuccessful) {
                    _state.value = ProductsState.Success(response.body()!!)
                } else {
                    _state.value = ProductsState.Error("Erro ao carregar produtos (${response.code()})")
                }
            } catch (e: Exception) {
                _state.value = ProductsState.Error("Falha de conexão: ${e.message}")
            }
        }
    }

    fun deleteProduct(id: Int, onSuccess: () -> Unit, onError: (String) -> Unit) {
        viewModelScope.launch {
            try {
                val response = RetrofitClient.instance.deleteProduct(id)
                if (response.isSuccessful) {
                    onSuccess()
                    loadProducts(_currentPage, _search)
                } else {
                    onError("Erro ao excluir produto (${response.code()})")
                }
            } catch (e: Exception) {
                onError("Falha de conexão: ${e.message}")
            }
        }
    }
}
