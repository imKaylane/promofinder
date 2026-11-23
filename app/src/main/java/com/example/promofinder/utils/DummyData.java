package com.example.promofinder.utils;

import com.example.promofinder.R;
import com.example.promofinder.models.Category;
import com.example.promofinder.models.PriceAlert;
import com.example.promofinder.models.PriceHistoryPoint;
import com.example.promofinder.models.Product;

import java.util.ArrayList;
import java.util.List;

public class DummyData {

    public static List<Category> getCategories() {
        List<Category> list = new ArrayList<>();
        list.add(new Category("cat_all", "Todas", R.drawable.ic_category, true));
        list.add(new Category("cat_inf", "Informática", R.drawable.ic_category, false));
        list.add(new Category("cat_hw", "Hardware", R.drawable.ic_category, false));
        list.add(new Category("cat_per", "Periféricos", R.drawable.ic_category, false));
        list.add(new Category("cat_game", "Games", R.drawable.ic_category, false));
        list.add(new Category("cat_inst", "Instrumentos M.", R.drawable.ic_category, false));
        list.add(new Category("cat_ele", "Eletrônicos", R.drawable.ic_category, false));
        list.add(new Category("cat_ace", "Acessórios", R.drawable.ic_category, false));
        return list;
    }

    public static List<Product> getDummyProducts() {
        List<Product> products = new ArrayList<>();

        // 1. Hardware / Informática
        Product p1 = new Product(
                "mlb_001",
                "Placa de Vídeo RTX 4070 Super 12GB GDDR6X Dual Fan",
                "Placa de vídeo NVIDIA GeForce RTX 4070 Super de alta performance para jogos em 1440p e ray tracing ativado. Arquitetura Ada Lovelace.",
                "https://http2.mlstatic.com/D_NQ_NP_978809-MLA74000355152_012024-O.webp",
                3899.00,
                4599.00,
                "Hardware",
                "Mercado Livre",
                "https://www.mercadolivre.com.br",
                "Hoje, 14:30"
        );
        p1.getPriceHistory().add(new PriceHistoryPoint("10/10", 4799.00));
        p1.getPriceHistory().add(new PriceHistoryPoint("15/10", 4599.00));
        p1.getPriceHistory().add(new PriceHistoryPoint("20/10", 4299.00));
        p1.getPriceHistory().add(new PriceHistoryPoint("Hoje", 3899.00));
        products.add(p1);

        // 2. Games
        Product p2 = new Product(
                "mlb_002",
                "Console PlayStation 5 Slim Edição Digital 1TB",
                "Console Sony PS5 Slim com 1TB de armazenamento SSD ultra rápido, controle sem fio DualSense e suporte a gráficos 4K HDR.",
                "https://http2.mlstatic.com/D_NQ_NP_890772-MLA73038622150_112023-O.webp",
                3499.90,
                3999.00,
                "Games",
                "Mercado Livre",
                "https://www.mercadolivre.com.br",
                "Hoje, 11:15"
        );
        p2.getPriceHistory().add(new PriceHistoryPoint("01/10", 4199.00));
        p2.getPriceHistory().add(new PriceHistoryPoint("12/10", 3999.00));
        p2.getPriceHistory().add(new PriceHistoryPoint("Hoje", 3499.90));
        products.add(p2);

        // 3. Periféricos
        Product p3 = new Product(
                "mlb_003",
                "Teclado Mecânico Gamer RGB Switches Red Anti-Ghosting",
                "Teclado mecânico ABNT2 com iluminação RGB personalizável, switches mecânicos de alta durabilidade e estrutura em alumínio.",
                "https://http2.mlstatic.com/D_NQ_NP_632128-MLB70492819030_072023-O.webp",
                249.90,
                389.00,
                "Periféricos",
                "Mercado Livre",
                "https://www.mercadolivre.com.br",
                "Há 2 horas"
        );
        p3.getPriceHistory().add(new PriceHistoryPoint("05/10", 389.00));
        p3.getPriceHistory().add(new PriceHistoryPoint("18/10", 319.00));
        p3.getPriceHistory().add(new PriceHistoryPoint("Hoje", 249.90));
        products.add(p3);

        // 4. Eletrônicos
        Product p4 = new Product(
                "mlb_004",
                "Monitor Gamer 27\" IPS 180Hz 1ms Full HD FreeSync",
                "Monitor de alta taxa de atualização com painel IPS, tecnologia AMD FreeSync, suporte VESA e bordas ultra finas.",
                "https://http2.mlstatic.com/D_NQ_NP_753891-MLA74628283015_022024-O.webp",
                999.00,
                1399.00,
                "Eletrônicos",
                "Mercado Livre",
                "https://www.mercadolivre.com.br",
                "Hoje, 09:00"
        );
        p4.getPriceHistory().add(new PriceHistoryPoint("01/10", 1499.00));
        p4.getPriceHistory().add(new PriceHistoryPoint("10/10", 1399.00));
        p4.getPriceHistory().add(new PriceHistoryPoint("Hoje", 999.00));
        products.add(p4);

        // 5. Informática
        Product p5 = new Product(
                "mlb_005",
                "Notebook Gamer Intel Core i7 16GB SSD 512GB RTX 3050",
                "Notebook de alta performance com tela 144Hz Full HD, teclado retroiluminado e sistema de refrigeração inteligente.",
                "https://http2.mlstatic.com/D_NQ_NP_832104-MLA72000122900_092023-O.webp",
                4299.00,
                5199.00,
                "Informática",
                "Mercado Livre",
                "https://www.mercadolivre.com.br",
                "Hoje, 13:10"
        );
        p5.getPriceHistory().add(new PriceHistoryPoint("01/10", 5499.00));
        p5.getPriceHistory().add(new PriceHistoryPoint("15/10", 5199.00));
        p5.getPriceHistory().add(new PriceHistoryPoint("Hoje", 4299.00));
        products.add(p5);

        // 6. Instrumentos Musicais
        Product p6 = new Product(
                "mlb_006",
                "Guitarra Eletroacústica Tagima Nylon com Afinador",
                "Guitarra acústica de alta qualidade sonora, braço confortável em cedro, captador de 4 bandas e afinador digital embutido.",
                "https://http2.mlstatic.com/D_NQ_NP_612849-MLB51299831902_082022-O.webp",
                899.00,
                1190.00,
                "Instrumentos M.",
                "Mercado Livre",
                "https://www.mercadolivre.com.br",
                "Ontem"
        );
        p6.getPriceHistory().add(new PriceHistoryPoint("01/10", 1190.00));
        p6.getPriceHistory().add(new PriceHistoryPoint("Hoje", 899.00));
        products.add(p6);

        // 7. Acessórios
        Product p7 = new Product(
                "mlb_007",
                "Fone de Ouvido Bluetooth TWS com Cancelamento de Ruído",
                "Headphone sem fio com estojo de carregamento com display LED, autonomia de até 30 horas de bateria e IPX5 resistente à água.",
                "https://http2.mlstatic.com/D_NQ_NP_908312-MLB71203912039_082023-O.webp",
                129.90,
                219.00,
                "Acessórios",
                "Mercado Livre",
                "https://www.mercadolivre.com.br",
                "Hoje, 10:00"
        );
        p7.getPriceHistory().add(new PriceHistoryPoint("10/10", 219.00));
        p7.getPriceHistory().add(new PriceHistoryPoint("Hoje", 129.90));
        products.add(p7);

        return products;
    }

    public static List<PriceAlert> getDummyAlerts() {
        List<PriceAlert> list = new ArrayList<>();
        List<Product> products = getDummyProducts();

        if (products.size() >= 2) {
            list.add(new PriceAlert("alert_01", products.get(0), 3700.00, true, "15/10/2024"));
            list.add(new PriceAlert("alert_02", products.get(2), 220.00, true, "18/10/2024"));
        }
        return list;
    }
}
