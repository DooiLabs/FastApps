import React from "react";
import { useWidgetProps } from "fastapps";
import useEmblaCarousel from "embla-carousel-react";
import { ArrowLeft, ArrowRight } from "lucide-react";
import Card from "./Card";
import "./index.css";

function {ClassName}() {
  const { cards } = useWidgetProps() || {};

  const normalizedCards = Array.isArray(cards) ? cards : [];
  const limitedCards = normalizedCards.slice(0, 8);
  const hasCards = limitedCards.length > 0;

  const [emblaRef, emblaApi] = useEmblaCarousel({
    align: "center",
    loop: false,
    containScroll: "trimSnaps",
    slidesToScroll: "auto",
    dragFree: false,
  });

  const [canPrev, setCanPrev] = React.useState(false);
  const [canNext, setCanNext] = React.useState(false);

  React.useEffect(() => {
    if (!emblaApi) return;
    const updateButtons = () => {
      setCanPrev(emblaApi.canScrollPrev());
      setCanNext(emblaApi.canScrollNext());
    };
    updateButtons();
    emblaApi.on("select", updateButtons);
    emblaApi.on("reInit", updateButtons);
    return () => {
      emblaApi.off("select", updateButtons);
      emblaApi.off("reInit", updateButtons);
    };
  }, [emblaApi]);

  if (!hasCards) {
    return (
      <div className="antialiased relative w-full py-5">
        <div className="text-center text-sm text-black/80 dark:text-white/80 py-6">
          No items to display. Provide up to 8 entries for best results.
        </div>
      </div>
    );
  }

  return (
    <div className="antialiased relative w-full py-5">
      <div className="overflow-hidden" ref={emblaRef}>
        <div className="flex gap-4 items-stretch">
          {limitedCards.map((card, i) => (
            <div
              key={card.id}
              className={`shrink-0 ${i === 0 ? "ml-5" : ""} ${i === limitedCards.length - 1 ? "mr-5" : ""}`}
            >
              <Card card={card} />
            </div>
          ))}
        </div>
      </div>
      {canPrev && (
        <button
          aria-label="Previous carousel item"
          className="absolute left-2 top-1/2 -translate-y-1/2 z-10 inline-flex items-center justify-center h-8 w-8 rounded-full bg-white text-black shadow-sm ring-1 ring-black/10 hover:bg-black/5 dark:bg-white/10 dark:text-white dark:ring-white/20 dark:hover:bg-white/20"
          onClick={() => emblaApi && emblaApi.scrollPrev()}
          type="button"
        >
          <ArrowLeft
            strokeWidth={1.5}
            className="h-4.5 w-4.5"
            aria-hidden="true"
          />
        </button>
      )}
      {canNext && (
        <button
          aria-label="Next carousel item"
          className="absolute right-2 top-1/2 -translate-y-1/2 z-10 inline-flex items-center justify-center h-8 w-8 rounded-full bg-white text-black shadow-sm ring-1 ring-black/10 hover:bg-black/5 dark:bg-white/10 dark:text-white dark:ring-white/20 dark:hover:bg-white/20"
          onClick={() => emblaApi && emblaApi.scrollNext()}
          type="button"
        >
          <ArrowRight
            strokeWidth={1.5}
            className="h-4.5 w-4.5"
            aria-hidden="true"
          />
        </button>
      )}
    </div>
  );
}

export default {ClassName};
