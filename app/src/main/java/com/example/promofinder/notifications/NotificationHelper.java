package com.example.promofinder.notifications;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

import androidx.core.app.NotificationCompat;
import androidx.core.app.NotificationManagerCompat;

import com.example.promofinder.MainActivity;
import com.example.promofinder.R;
import com.example.promofinder.models.Product;
import com.example.promofinder.utils.FormatUtils;

public class NotificationHelper {
    public static final String CHANNEL_ID = "promo_alerts_channel";
    public static final String CHANNEL_NAME = "Alertas de Preço PromoFinder";
    public static final String CHANNEL_DESC = "Notificações quando um produto atinge o preço desejado ou tem grande desconto.";

    public static void createNotificationChannel(Context context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                    CHANNEL_ID,
                    CHANNEL_NAME,
                    NotificationManager.IMPORTANCE_HIGH
            );
            channel.setDescription(CHANNEL_DESC);
            NotificationManager manager = context.getSystemService(NotificationManager.class);
            if (manager != null) {
                manager.createNotificationChannel(channel);
            }
        }
    }

    public static void sendPriceDropNotification(Context context, Product product, double targetPrice) {
        createNotificationChannel(context);

        Intent intent = new Intent(context, MainActivity.class);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        PendingIntent pendingIntent = PendingIntent.getActivity(
                context, 0, intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );

        String title = "🔥 Alerta de Preço Atingido!";
        String message = product.getTitle() + " está por " + FormatUtils.formatCurrency(product.getCurrentPrice()) + " (meta: " + FormatUtils.formatCurrency(targetPrice) + ")!";

        NotificationCompat.Builder builder = new NotificationCompat.Builder(context, CHANNEL_ID)
                .setSmallIcon(R.drawable.ic_notifications)
                .setContentTitle(title)
                .setContentText(message)
                .setStyle(new NotificationCompat.BigTextStyle().bigText(message))
                .setPriority(NotificationCompat.PRIORITY_HIGH)
                .setContentIntent(pendingIntent)
                .setAutoCancel(true);

        NotificationManagerCompat notificationManager = NotificationManagerCompat.from(context);
        try {
            notificationManager.notify((int) System.currentTimeMillis(), builder.build());
        } catch (SecurityException ignored) {
            // Em Android 13+, caso permissão POST_NOTIFICATIONS não tenha sido concedida ainda
        }
    }
}
