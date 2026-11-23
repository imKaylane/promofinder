package com.example.promofinder.fragments;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import com.example.promofinder.databinding.FragmentProfileBinding;
import com.example.promofinder.models.User;
import com.example.promofinder.utils.PreferencesHelper;

public class ProfileFragment extends Fragment {

    private FragmentProfileBinding binding;
    private PreferencesHelper preferencesHelper;
    private User currentUser;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container,
                             @Nullable Bundle savedInstanceState) {
        binding = FragmentProfileBinding.inflate(inflater, container, false);
        return binding.getRoot();
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        preferencesHelper = new PreferencesHelper(requireContext());
        currentUser = preferencesHelper.getUserProfile();

        binding.txtUserName.setText(currentUser.getName());
        binding.txtUserEmail.setText(currentUser.getEmail());

        binding.switchPriceAlerts.setChecked(currentUser.isPriceAlertsEnabled());
        binding.switchPromos.setChecked(currentUser.isPromoNotificationsEnabled());

        binding.switchPriceAlerts.setOnCheckedChangeListener((buttonView, isChecked) -> {
            currentUser.setPriceAlertsEnabled(isChecked);
            preferencesHelper.saveUserProfile(currentUser);
            Toast.makeText(getContext(), "Preferência atualizada", Toast.LENGTH_SHORT).show();
        });

        binding.switchPromos.setOnCheckedChangeListener((buttonView, isChecked) -> {
            currentUser.setPromoNotificationsEnabled(isChecked);
            preferencesHelper.saveUserProfile(currentUser);
            Toast.makeText(getContext(), "Preferência atualizada", Toast.LENGTH_SHORT).show();
        });
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();
        binding = null;
    }
}
