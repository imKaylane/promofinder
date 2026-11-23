package com.example.promofinder.adapters;

import android.view.LayoutInflater;
import android.view.ViewGroup;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.bumptech.glide.Glide;
import com.example.promofinder.R;
import com.example.promofinder.databinding.ItemPriceAlertBinding;
import com.example.promofinder.models.PriceAlert;
import com.example.promofinder.utils.FormatUtils;

import java.util.ArrayList;
import java.util.List;

public class PriceAlertAdapter extends RecyclerView.Adapter<PriceAlertAdapter.AlertViewHolder> {

    public interface OnAlertClickListener {
        void onAlertClick(PriceAlert alert);
        void onDeleteClick(PriceAlert alert);
        void onToggleActive(PriceAlert alert, boolean isActive);
    }

    private List<PriceAlert> alerts;
    private final OnAlertClickListener listener;

    public PriceAlertAdapter(List<PriceAlert> alerts, OnAlertClickListener listener) {
        this.alerts = alerts != null ? alerts : new ArrayList<>();
        this.listener = listener;
    }

    public void setAlerts(List<PriceAlert> alerts) {
        this.alerts = alerts != null ? alerts : new ArrayList<>();
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public AlertViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        ItemPriceAlertBinding binding = ItemPriceAlertBinding.inflate(
                LayoutInflater.from(parent.getContext()), parent, false);
        return new AlertViewHolder(binding);
    }

    @Override
    public void onBindViewHolder(@NonNull AlertViewHolder holder, int position) {
        holder.bind(alerts.get(position));
    }

    @Override
    public int getItemCount() {
        return alerts.size();
    }

    class AlertViewHolder extends RecyclerView.ViewHolder {
        private final ItemPriceAlertBinding binding;

        public AlertViewHolder(@NonNull ItemPriceAlertBinding binding) {
            super(binding.getRoot());
            this.binding = binding;
        }

        public void bind(PriceAlert alert) {
            if (alert.getProduct() != null) {
                binding.txtAlertProductTitle.setText(alert.getProduct().getTitle());
                binding.txtAlertCurrentPrice.setText("Atual: " + FormatUtils.formatCurrency(alert.getProduct().getCurrentPrice()));

                Glide.with(itemView.getContext())
                        .load(alert.getProduct().getImageUrl())
                        .placeholder(R.drawable.ic_launcher_background)
                        .error(R.drawable.ic_launcher_background)
                        .into(binding.imgAlertProduct);
            }

            binding.txtAlertTargetPrice.setText("Preço Desejado: " + FormatUtils.formatCurrency(alert.getTargetPrice()));
            binding.switchAlertActive.setChecked(alert.isActive());

            binding.switchAlertActive.setOnCheckedChangeListener((buttonView, isChecked) -> {
                alert.setActive(isChecked);
                if (listener != null) {
                    listener.onToggleActive(alert, isChecked);
                }
            });

            binding.btnDeleteAlert.setOnClickListener(v -> {
                if (listener != null) {
                    listener.onDeleteClick(alert);
                }
            });

            itemView.setOnClickListener(v -> {
                if (listener != null) {
                    listener.onAlertClick(alert);
                }
            });
        }
    }
}
