package com.example.promofinder.fragments;

import android.content.Intent;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;

import com.example.promofinder.activities.ProductDetailsActivity;
import com.example.promofinder.adapters.PriceAlertAdapter;
import com.example.promofinder.databinding.FragmentPriceAlertsBinding;
import com.example.promofinder.models.PriceAlert;
import com.example.promofinder.models.Product;
import com.example.promofinder.notifications.NotificationHelper;
import com.example.promofinder.utils.DummyData;
import com.example.promofinder.utils.PreferencesHelper;

import java.util.List;

public class PriceAlertsFragment extends Fragment implements PriceAlertAdapter.OnAlertClickListener {

    private FragmentPriceAlertsBinding binding;
    private PreferencesHelper preferencesHelper;
    private PriceAlertAdapter adapter;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container,
                             @Nullable Bundle savedInstanceState) {
        binding = FragmentPriceAlertsBinding.inflate(inflater, container, false);
        return binding.getRoot();
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        preferencesHelper = new PreferencesHelper(requireContext());
        setupRecyclerView();
        setupListeners();
    }

    @Override
    public void onResume() {
        super.onResume();
        loadAlerts();
    }

    private void setupRecyclerView() {
        binding.rvAlerts.setLayoutManager(new LinearLayoutManager(getContext()));
        adapter = new PriceAlertAdapter(null, this);
        binding.rvAlerts.setAdapter(adapter);
    }

    private void setupListeners() {
        binding.btnSimulateAlert.setOnClickListener(v -> {
            List<PriceAlert> alerts = preferencesHelper.getPriceAlerts();
            if (!alerts.isEmpty()) {
                PriceAlert alert = alerts.get(0);
                NotificationHelper.sendPriceDropNotification(requireContext(), alert.getProduct(), alert.getTargetPrice());
                Toast.makeText(getContext(), "Notificação simulada enviada!", Toast.LENGTH_SHORT).show();
            } else {
                List<Product> products = DummyData.getDummyProducts();
                if (!products.isEmpty()) {
                    Product sample = products.get(0);
                    NotificationHelper.sendPriceDropNotification(requireContext(), sample, sample.getCurrentPrice() * 0.9);
                    Toast.makeText(getContext(), "Notificação de oferta enviada!", Toast.LENGTH_SHORT).show();
                }
            }
        });
    }

    private void loadAlerts() {
        List<PriceAlert> alerts = preferencesHelper.getPriceAlerts();
        // Se estiver vazio no primeiro uso, adiciona alertas demonstrativos
        if (alerts.isEmpty()) {
            List<PriceAlert> dummyAlerts = DummyData.getDummyAlerts();
            for (PriceAlert a : dummyAlerts) {
                preferencesHelper.savePriceAlert(a);
            }
            alerts = preferencesHelper.getPriceAlerts();
        }

        if (alerts.isEmpty()) {
            binding.rvAlerts.setVisibility(View.GONE);
            binding.layoutEmptyAlerts.setVisibility(View.VISIBLE);
        } else {
            binding.rvAlerts.setVisibility(View.VISIBLE);
            binding.layoutEmptyAlerts.setVisibility(View.GONE);
            adapter.setAlerts(alerts);
        }
    }

    @Override
    public void onAlertClick(PriceAlert alert) {
        if (alert.getProduct() != null) {
            Intent intent = new Intent(getContext(), ProductDetailsActivity.class);
            intent.putExtra("product", alert.getProduct());
            startActivity(intent);
        }
    }

    @Override
    public void onDeleteClick(PriceAlert alert) {
        preferencesHelper.removePriceAlert(alert.getId());
        loadAlerts();
        Toast.makeText(getContext(), "Alerta removido com sucesso", Toast.LENGTH_SHORT).show();
    }

    @Override
    public void onToggleActive(PriceAlert alert, boolean isActive) {
        alert.setActive(isActive);
        preferencesHelper.savePriceAlert(alert);
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();
        binding = null;
    }
}
