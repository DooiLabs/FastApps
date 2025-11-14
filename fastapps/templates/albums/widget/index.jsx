import React from "react";
import { useWidgetProps, useMaxHeight, useOpenAiGlobal } from "fastapps";
import useEmblaCarousel from "embla-carousel-react";
import { ArrowLeft, ArrowRight } from "lucide-react";
import FullscreenViewer from "./FullscreenViewer";
import AlbumCard from "./AlbumCard";
import "./index.css";

function AlbumsCarousel({ albums, onSelect }) {
  const normalizedAlbums = Array.isArray(albums)
    ? albums.filter((album) => album && album.cover)
    : [];
  const hasMinimumItems = normalizedAlbums.length >= 3;
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

  if (!hasMinimumItems) {
    return (
      <div className="antialiased relative w-full py-5">
        <div className="text-center text-sm text-black/80 dark:text-white/80 py-6">
          Provide between 3 and 8 albums with covers to enable the gallery.
        </div>
      </div>
    );
  }

  return (
    <div className="antialiased relative w-full text-black py-5 select-none">
      <div className="overflow-hidden" ref={emblaRef}>
        <div className="flex gap-5 items-stretch">
          {normalizedAlbums.map((album, i) => (
            <div
              key={album.id}
              className={`shrink-0 ${i === 0 ? "ml-6" : ""} ${i === normalizedAlbums.length - 1 ? "mr-6" : ""}`}
            >
              <AlbumCard album={album} onSelect={onSelect} />
            </div>
          ))}
        </div>
      </div>
      <div
        aria-hidden
        className={
          "pointer-events-none absolute inset-y-0 left-0 w-3 z-[5] transition-opacity duration-200 " +
          (canPrev ? "opacity-100" : "opacity-0")
        }
      >
        <div
          className="h-full w-full border-l border-black/15 bg-gradient-to-r from-black/10 to-transparent"
          style={{
            WebkitMaskImage:
              "linear-gradient(to bottom, transparent 0%, white 30%, white 70%, transparent 100%)",
            maskImage:
              "linear-gradient(to bottom, transparent 0%, white 30%, white 70%, transparent 100%)",
          }}
        />
      </div>
      <div
        aria-hidden
        className={
          "pointer-events-none absolute inset-y-0 right-0 w-3 z-[5] transition-opacity duration-200 " +
          (canNext ? "opacity-100" : "opacity-0")
        }
      >
        <div
          className="h-full w-full border-r border-black/15 bg-gradient-to-l from-black/10 to-transparent"
          style={{
            WebkitMaskImage:
              "linear-gradient(to bottom, transparent 0%, white 30%, white 70%, transparent 100%)",
            maskImage:
              "linear-gradient(to bottom, transparent 0%, white 30%, white 70%, transparent 100%)",
          }}
        />
      </div>
      {canPrev && (
        <button
          aria-label="Previous"
          className="absolute left-2 top-1/2 -translate-y-1/2 z-10 inline-flex items-center justify-center h-8 w-8 rounded-full bg-white text-black shadow-lg ring ring-black/5 hover:bg-white"
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
          aria-label="Next"
          className="absolute right-2 top-1/2 -translate-y-1/2 z-10 inline-flex items-center justify-center h-8 w-8 rounded-full bg-white text-black shadow-lg ring ring-black/5 hover:bg-white"
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

function {ClassName}() {
  const { albums } = useWidgetProps() || {};
  const normalizedAlbums = Array.isArray(albums)
    ? albums
        .filter((album) => album && album.cover)
        .map((album) => ({
          ...album,
          photos: Array.isArray(album.photos) ? album.photos : [],
        }))
    : [];
  const limitedAlbums = normalizedAlbums.slice(0, 8);
  const displayMode = useOpenAiGlobal("displayMode");
  const isFullscreen = displayMode === "fullscreen";
  const [selectedAlbum, setSelectedAlbum] = React.useState(null);
  const maxHeight = useMaxHeight() ?? undefined;

  React.useEffect(() => {
    if (!selectedAlbum) {
      return;
    }
    const stillExists = limitedAlbums.some((album) => album.id === selectedAlbum.id);
    if (!stillExists) {
      setSelectedAlbum(null);
      if (window?.openai?.requestDisplayMode) {
        window.openai.requestDisplayMode({ mode: "inline" });
      }
    }
  }, [limitedAlbums, selectedAlbum]);

  const handleSelectAlbum = (album) => {
    if (!album) return;
    setSelectedAlbum(album);
    if (window?.openai?.requestDisplayMode) {
      window.openai.requestDisplayMode({ mode: "fullscreen" });
    }
  };

  const handleBackToAlbums = () => {
    setSelectedAlbum(null);
    if (window?.openai?.requestDisplayMode) {
      window.openai.requestDisplayMode({ mode: "inline" });
    }
  };

  return (
    <div
      className={
        "relative antialiased w-full " +
        (isFullscreen
          ? "bg-white"
          : "bg-transparent border border-black/10 rounded-3xl overflow-hidden")
      }
      style={{
        maxHeight,
        height: isFullscreen ? maxHeight : undefined,
      }}
    >
      {!isFullscreen && (
        <AlbumsCarousel albums={limitedAlbums} onSelect={handleSelectAlbum} />
      )}

      {isFullscreen && selectedAlbum && (
        <FullscreenViewer album={selectedAlbum} onBack={handleBackToAlbums} />
      )}
    </div>
  );
}

export default {ClassName};
