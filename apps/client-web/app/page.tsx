import { CategoriesList } from "../components/CategoriesList";
import { Hero } from "../components/Hero";
import { NewsList } from "../components/NewsList";
import { ProductCard } from "../components/ProductCard";
import { SectionHeading } from "../components/SectionHeading";
import { getLandingData } from "../lib/api";

export default async function Home() {
  const { categories, products, news } = await getLandingData();

  return (
    <main>
      <Hero />

      <section id="catalog">
        <SectionHeading
          overline="Каталог"
          title="Соберите структуру магазина"
          description="Категории наследуют древовидную модель, поддерживают SEO-метаданные и позиционирование."
        />
        <div className="grid" style={{ gap: "2rem" }}>
          <div>
            <h3>Структура каталога</h3>
            <p className="muted">Добавляйте, скрывайте и перемещайте ветви дерева без миграций.</p>
            <CategoriesList categories={categories} />
          </div>
          <div style={{ flex: 1 }}>
            <h3>Популярные товары</h3>
            <div className="grid grid-3">
              {products.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          </div>
        </div>
      </section>

      <section id="news">
        <SectionHeading
          overline="Новости"
          title="Единый changelog для команды"
          description="Публикуйте новости для клиентов и ведите историю изменений для команды разработки."
        />
        <NewsList news={news} />
      </section>

      <section>
        <SectionHeading
          overline="Доставка и оплаты"
          title="Платёжные и логистические методы"
          description="Управляйте провайдерами эквайринга, логотипами и SLA прямо из администратора."
        />
        <div className="grid grid-3">
          {["Платежи", "Доставка", "Получатели"].map((card) => (
            <article key={card} className="card">
              <h3>{card}</h3>
              <p className="muted">
                API предоставляет CRUD по методам, тарифам и получателям, что упрощает интеграцию с
                фронтендом и мобильными клиентами.
              </p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}


