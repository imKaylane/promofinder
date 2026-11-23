package com.example.promofinder.utils;

public class DiscountCalculator {

    public static int calculateDiscountPercentage(double currentPrice, double previousPrice) {
        if (previousPrice <= 0 || previousPrice <= currentPrice) {
            return 0;
        }
        double discount = ((previousPrice - currentPrice) / previousPrice) * 100.0;
        return (int) Math.round(discount);
    }
}
