import React from "react";

function AlbumCard({ album, onSelect }) {
  if (!album) return null;

  const photoCount = Array.isArray(album.photos) ? album.photos.length : 0;
  const photoSummary = photoCount > 0 ? `${photoCount} photos` : "View album";
  const title = album.title || "Album";

  return (
    <button
      type="button"
      className="group relative cursor-pointer flex-shrink-0 w-[272px] bg-white dark:bg-white/5 text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-black/40 dark:focus-visible:ring-white/40 rounded-3xl"
      onClick={() => onSelect?.(album)}
      aria-label={`Open ${title}`}
    >
      <div className="aspect-[4/3] w-full overflow-hidden rounded-2xl shadow-lg">
        <img
          src={album.cover}
          alt={title}
          className="h-full w-full object-cover"
          loading="lazy"
        />
      </div>
      <div className="pt-3 px-1.5">
        <div className="text-base font-medium truncate text-black dark:text-white">{title}</div>
        <div className="text-sm text-black/80 dark:text-white/80 mt-0.5">{photoSummary}</div>
      </div>
    </button>
  );
}

export default AlbumCard;
