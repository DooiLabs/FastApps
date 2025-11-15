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
  const hasAlbums = normalizedAlbums.length > 0;
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

  if (!hasAlbums) {
    return (
      <div className="antialiased relative w-full py-5">
        <div className="text-center text-sm text-black/80 dark:text-white/80 py-6">
          No albums available. Provide up to 8 entries for best results.
        </div>
      </div>
    );
  }

  return (
    <div className="antialiased relative w-full text-black dark:text-white py-5 select-none">
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
      {canPrev && (
        <button
          aria-label="Previous"
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
          aria-label="Next"
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
        "relative antialiased w-full text-black dark:text-white " +
        (isFullscreen
          ? "bg-white"
          : "bg-transparent overflow-hidden")
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
