import React from "react";
import { useWidgetProps } from "fastapps";
import { PlusCircle, Star } from "lucide-react";
import "./index.css";

function {ClassName}() {
  const { title, description, items } = useWidgetProps() || {};
  const normalizedItems = Array.isArray(items) ? items.slice(0, 7) : [];
  const hasItems = normalizedItems.length > 0;

  return (
    <div className="antialiased w-full text-black dark:text-white px-4 pb-2 border border-black/10 dark:border-white/10 rounded-2xl sm:rounded-3xl overflow-hidden bg-white dark:bg-white/5">
      <div className="max-w-full">
        <div className="flex flex-col sm:flex-row sm:items-center gap-4 border-b border-black/5 dark:border-white/10 py-4">
          <div className="flex flex-col gap-1">
            <div className="text-base sm:text-xl font-medium">
              {title || "List Title"}
            </div>
            <div className="text-sm text-black/80 dark:text-white/80">
              {description || "A list of items"}
            </div>
          </div>
          <div className="sm:ml-auto">
            <button
              type="button"
              className="cursor-pointer inline-flex items-center rounded-full border border-black/20 dark:border-white/20 bg-white text-black dark:bg-white/10 dark:text-white px-4 py-1.5 text-sm font-medium hover:bg-black/5 active:bg-black/10 dark:hover:bg-white/20"
            >
              Save list
            </button>
          </div>
        </div>
        <ol className="min-w-full text-sm flex flex-col divide-y divide-black/10 dark:divide-white/10">
          {normalizedItems.map((item, i) => {
            const rank = i + 1;
            const infoText = item?.info || "–";
            return (
              <li key={item?.id || i} className="px-1 sm:px-2">
                <div className="flex w-full items-center gap-3 py-3">
                  <div className="font-medium text-black/80 dark:text-white/80 hidden sm:block w-4 text-right">
                    {rank}
                  </div>
                  <div className="flex items-center gap-3 min-w-0 flex-1">
                    <img
                      src={item?.thumbnail || "https://via.placeholder.com/44"}
                      alt={item?.name || `Item ${rank}`}
                      className="h-10 w-10 sm:h-11 sm:w-11 rounded-lg object-cover ring ring-black/5 dark:ring-white/10"
                      loading="lazy"
                    />
                    <div className="min-w-0 flex flex-col">
                      <div className="font-medium text-sm sm:text-base truncate max-w-[40ch]">
                        {item?.name || `Item ${rank}`}
                      </div>
                      <div className="mt-1 flex items-center gap-3 text-black/80 dark:text-white/80 text-sm">
                        <div className="flex items-center gap-1">
                          <Star strokeWidth={1.5} className="h-3 w-3" aria-hidden="true" />
                          <span>
                            {typeof item?.rating === "number"
                              ? item.rating.toFixed(1)
                              : item?.rating || "–"}
                          </span>
                        </div>
                        <div className="whitespace-nowrap sm:hidden">{infoText}</div>
                      </div>
                    </div>
                  </div>
                  <div className="hidden sm:block text-sm text-black/80 dark:text-white/80 whitespace-nowrap">
                    {infoText}
                  </div>
                  <div className="flex justify-end">
                    <button
                      type="button"
                      className="inline-flex items-center gap-1 rounded-full border border-black/20 dark:border-white/20 px-3 py-1 text-sm font-medium text-black dark:text-white hover:bg-black/5 active:bg-black/10 dark:hover:bg-white/20"
                      aria-label={`Add ${item?.name || `item ${rank}`} to list`}
                    >
                      <PlusCircle strokeWidth={1.5} className="h-4 w-4" aria-hidden="true" />
                      <span>Add</span>
                    </button>
                  </div>
                </div>
              </li>
            );
          })}
        </ol>
        {!hasItems && (
          <div className="py-6 text-center text-black/80 dark:text-white/80">
            No items available. Provide up to 7 entries for best results.
          </div>
        )}
      </div>
    </div>
  );
}

export default {ClassName};
