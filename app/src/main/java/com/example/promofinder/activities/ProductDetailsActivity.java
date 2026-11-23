package com.example.promofinder.activities;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;

import com.bumptech.glide.Glide;
import com.example.promofinder.R;
import com.example.promofinder.databinding.ActivityProductDetailsBinding;
import com.example.promofinder.databinding.ItemPriceHistoryPointBinding;
import com.example.promofinder.models.PriceAlert;
import com.example.promofinder.models.PriceHistoryPoint;
import com.example.promofinder.models.Product;
import com.example.promofinder.utils.FormatUtils;
import com.example.promofinder.utils.PreferencesHelper;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class ProductDetailsActivity extends AppCompatActivity {

    private ActivityProductDetailsBinding binding;
    private PreferencesHelper preferencesHelper;
    private Product product;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivityProductDetailsBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());

        preferencesHelper = new PreferencesHelper(this);

        product = (Product) getIntent().getSerializableExtra("product");
        if (product == null) {
            Toast.makeText(this, "Produto indisponível", Toast.LENGTH_SHORT).show();
            finish();
            return;
        }

        bindProductData();
        setupListeners();
    }

    private void bindProductData() {
        binding.txtTitleDetail.setText(product.getTitle());
        binding.txtDescriptionDetail.setText(product.getDescription() != null ? product.getDescription() : "Sem descrição disponível.");
        binding.txtMarketplaceDetail.setText(product.getMarketplace());
        binding.txtCategoryDetail.setText(product.getCategory());
        binding.txtCurrentPriceDetail.setText(FormatUtils.formatCurrency(product.getCurrentPrice()));

        if (product.getPreviousPrice() > product.getCurrentPrice()) {
            binding.txtPreviousPriceDetail.setVisibility(View.VISIBLE);
            binding.txtPreviousPriceDetail.setText("De " + FormatUtils.formatCurrency(product.getPreviousPrice()));
            binding.txtPreviousPriceDetail.setPaintFlags(binding.txtPreviousPriceDetail.getPaintFlags() | android.graphics.Paint.STRIKE_THRU_TEXT_FLAG);

            binding.txtDiscountDetail.setVisibility(View.VISIBLE);
            binding.txtDiscountDetail.setText(FormatUtils.formatDiscount(product.getDiscountPercentage()));
        } else {
            binding.txtPreviousPriceDetail.setVisibility(View.GONE);
            binding.txtDiscountDetail.setVisibility(View.GONE);
        }

        binding.txtLastUpdated.setText("Última verificação: " + (product.getLastUpdated() != null ? product.getLastUpdated() : "Hoje"));

        // Image
        Glide.with(this)
                .load(product.getImageUrl())
                .placeholder(R.drawable.ic_launcher_background)
                .error(R.drawable.ic_launcher_background)
                .into(binding.imgProductDetail);

        // Favorite State
        updateFavoriteButtonState();

        // Price History
        renderPriceHistory();
    }

    private void updateFavoriteButtonState() {
        boolean isFav = preferencesHelper.isFavorite(product.getId());
        binding.btnFavDetail.setImageResource(isFav ? R.drawable.ic_favorite_filled : R.drawable.ic_favorite);
    }

    private void renderPriceHistory() {
        binding.layoutPriceHistoryContainer.removeAllViews();
        if (product.getPriceHistory() != null && !product.getPriceHistory().isEmpty()) {
            for (PriceHistoryPoint pt : product.getPriceHistory()) {
                ItemPriceHistoryPointBinding historyBinding = ItemPriceHistoryPointBinding.inflate(
                        LayoutInflater.from(this), binding.layoutPriceHistoryContainer, false);

                historyBinding.txtHistoryDate.setText(pt.getDate());
                historyBinding.txtHistoryPrice.setText(FormatUtils.formatCurrency(pt.getPrice()));

                binding.layoutPriceHistoryContainer.addView(historyBinding.getRoot());
            }
        } else {
            ItemPriceHistoryPointBinding historyBinding = ItemPriceHistoryPointBinding.inflate(
                    LayoutInflater.from(this), binding.layoutPriceHistoryContainer, false);
            historyBinding.txtHistoryDate.setText("Hoje");
            historyBinding.txtHistoryPrice.setText(FormatUtils.formatCurrency(product.getCurrentPrice()));
            binding.layoutPriceHistoryContainer.addView(historyBinding.getRoot());
        }
    }

    private void setupListeners() {
        binding.btnBack.setOnClickListener(v -> finish());

        binding.btnFavDetail.setOnClickListener(v -> {
            boolean isFav = preferencesHelper.isFavorite(product.getId());
            if (isFav) {
                preferencesHelper.removeFavorite(product.getId());
                Toast.makeText(this, "Removido dos favoritos", Toast.LENGTH_SHORT).show();
            } else {
                preferencesHelper.addFavorite(product);
                Toast.makeText(this, "Adicionado aos favoritos", Toast.LENGTH_SHORT).show();
            }
            updateFavoriteButtonState();
        });

        binding.btnOpenOfferMain.setOnClickListener(v -> openOfferInBrowser());

        binding.btnTrackPrice.setOnClickListener(v -> showPriceAlertDialog());
    }

    private void openOfferInBrowser() {
        if (product.getProductUrl() != null && !product.getProductUrl().isEmpty()) {
            Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(product.getProductUrl()));
            startActivity(intent);
        } else {
            Toast.makeText(this, "URL da oferta indisponível", Toast.LENGTH_SHORT).show();
        }
    }

    private void showPriceAlertDialog() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this, R.style.Theme_PromoFinder);
        builder.setTitle("Criar Alerta de Preço");

        View dialogView = LayoutInflater.from(this).inflate(R.layout.dialog_set_price_alert, null);
        EditText etTargetPrice = dialogView.findViewById(R.id.etDialogTargetPrice);
        etTargetPrice.setText(String.format(Locale.US, "%.2f", product.getCurrentPrice() * 0.9));

        builder.setView(dialogView);
        builder.setPositiveButton("Ativar Alerta", (dialog, which) -> {
            String input = etTargetPrice.getText().toString().trim();
            if (!input.isEmpty()) {
                try {
                    double targetPrice = Double.parseDouble(input);
                    String date = new SimpleDateFormat("dd/MM/yyyy", Locale.getDefault()).format(new Date());
                    PriceAlert alert = new PriceAlert("alert_" + System.currentTimeMillis(), product, targetPrice, true, date);
                    preferencesHelper.savePriceAlert(alert);
                    Toast.makeText(this, "Alerta de preço ativado para " + FormatUtils.formatCurrency(targetPrice) + "!", Toast.LENGTH_LONG).show();
                } catch (NumberFormatException e) {
                    Toast.makeText(this, "Valor inválido", Toast.LENGTH_SHORT).show();
                }
            }
        });
        builder.setNegativeButton("Cancelar", null);
        builder.show();
    }
}
