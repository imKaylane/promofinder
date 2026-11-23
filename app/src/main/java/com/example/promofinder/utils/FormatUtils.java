package com.example.promofinder.utils;

import java.text.NumberFormat;
import java.util.Locale;

public class FormatUtils {

    public static String formatCurrency(double amount) {
        NumberFormat formatter = NumberFormat.getCurrencyInstance(new Locale("pt", "BR"));
        return formatter.format(amount);
    }

    public static String formatDiscount(int discountPercentage) {
        return discountPercentage + "% OFF";
    }
}
