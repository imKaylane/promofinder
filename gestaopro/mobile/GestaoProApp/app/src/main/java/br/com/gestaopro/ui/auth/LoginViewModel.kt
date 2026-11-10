// GestãoPro — LoginViewModel.kt
// ViewModel para autenticação (EX5/EX7 — MVVM)
package br.com.gestaopro.ui.auth

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import br.com.gestaopro.data.api.RetrofitClient
import br.com.gestaopro.data.model.LoginRequest
import br.com.gestaopro.util.SecureStorage
import kotlinx.coroutines.launch

sealed class LoginState {
    object Idle    : LoginState()
    object Loading : LoginState()
    data class Success(val userName: String) : LoginState()
    data class Error(val message: String) : LoginState()
}

class LoginViewModel : ViewModel() {

    private val _state = MutableLiveData<LoginState>(LoginState.Idle)
    val state: LiveData<LoginState> = _state

    fun login(email: String, password: String) {
        if (email.isBlank() || password.isBlank()) {
            _state.value = LoginState.Error("E-mail e senha são obrigatórios")
            return
        }

        _state.value = LoginState.Loading
        viewModelScope.launch {
            try {
                val response = RetrofitClient.instance.login(LoginRequest(email, password))
                if (response.isSuccessful) {
                    val body = response.body()!!
                    SecureStorage.saveTokens(body.accessToken, body.refreshToken)

                    // Busca o perfil do usuário
                    val meResponse = RetrofitClient.instance.getMe()
                    val name = if (meResponse.isSuccessful) meResponse.body()?.name ?: "" else ""
                    _state.value = LoginState.Success(name)
                } else {
                    _state.value = LoginState.Error(
                        when (response.code()) {
                            401 -> "Credenciais inválidas"
                            else -> "Erro ao fazer login (${response.code()})"
                        }
                    )
                }
            } catch (e: Exception) {
                _state.value = LoginState.Error("Falha de conexão: ${e.message ?: "Verifique a rede"}")
            }
        }
    }
}
