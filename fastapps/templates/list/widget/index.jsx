import React, { useEffect } from "react";
import { useWidgetProps } from "fastapps";
import { PlusCircle, Star } from "lucide-react";
import "./index.css";

function {ClassName}() {
  const widgetProps = useWidgetProps();
  const items = widgetProps?.items || [];

  useEffect(() => {
    if (widgetProps) {
      console.log('List widget props:', widgetProps);
    }
  }, [widgetProps]);

  return (
    <div className="antialiased w-full text-black px-4 pb-2 border border-black/10 rounded-2xl sm:rounded-3xl overflow-hidden bg-white">
      <div className="max-w-full">
        <div className="flex flex-row items-center gap-4 sm:gap-4 border-b border-black/5 py-4">
          <div
            className="sm:w-18 w-16 aspect-square rounded-xl bg-cover bg-center"
            style={{
              backgroundImage:
                "url(https://pub-d9760dbd87764044a85486be2fdf7f9f.r2.dev/fastapps.png)",
            }}
          ></div>
          <div>
            <div className="text-base sm:text-xl font-medium">
              {widgetProps?.title || "List Title"}
            </div>
            <div className="text-sm text-black/60">
              {widgetProps?.description || "A list of items"}
            </div>
          </div>
          <div className="flex-auto hidden sm:flex justify-end pr-2">
            <button
              type="button"
              className="cursor-pointer inline-flex items-center rounded-full bg-[#010304] text-white px-4 py-1.5 sm:text-md text-sm font-medium hover:opacity-90 active:opacity-100"
            >
              Save List
            </button>
          </div>
        </div>
        <div className="min-w-full text-sm flex flex-col">
          {items.slice(0, 7).map((item, i) => (
            <div
              key={item.id || i}
              className="px-3 -mx-2 rounded-2xl hover:bg-black/5"
            >
              <div
                style={{
                  borderBottom:
                    i === 7 - 1 ? "none" : "1px solid rgba(0, 0, 0, 0.05)",
                }}
                className="flex w-full items-center hover:border-black/0! gap-2"
              >
                <div className="py-3 pr-3 min-w-0 w-full sm:w-3/5">
                  <div className="flex items-center gap-3">
                    <img
                      src={item.thumbnail || "https://via.placeholder.com/44"}
                      alt={item.name}
                      className="h-10 w-10 sm:h-11 sm:w-11 rounded-lg object-cover ring ring-black/5"
                    />
                    <div className="w-3 text-end sm:block hidden text-sm text-black/40">
                      {i + 1}
                    </div>
                    <div className="min-w-0 sm:pl-1 flex flex-col items-start h-full">
                      <div className="font-medium text-sm sm:text-md truncate max-w-[40ch]">
                        {item.name}
                      </div>
                      <div className="mt-1 sm:mt-0.25 flex items-center gap-3 text-black/70 text-sm">
                        <div className="flex items-center gap-1">
                          <Star
                            strokeWidth={1.5}
                            className="h-3 w-3 text-black"
                          />
                          <span>
                            {item.rating?.toFixed
                              ? item.rating.toFixed(1)
                              : item.rating}
                          </span>
                        </div>
                        <div className="whitespace-nowrap sm:hidden">
                          {item.info || "–"}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="hidden sm:block text-end py-2 px-3 text-sm text-black/60 whitespace-nowrap flex-auto">
                  {item.info || "–"}
                </div>
                <div className="py-2 whitespace-nowrap flex justify-end">
                  <PlusCircle strokeWidth={1.5} className="h-5 w-5" />
                </div>
              </div>
            </div>
          ))}
          {items.length === 0 && (
            <div className="py-6 text-center text-black/60">
              No items found.
            </div>
          )}
        </div>
        <div className="sm:hidden px-0 pt-2 pb-2">
          <button
            type="button"
            className="w-full cursor-pointer inline-flex items-center justify-center rounded-full bg-[#F46C21] text-white px-4 py-2 font-medium hover:opacity-90 active:opacity-100"
          >
            Save List
          </button>
        </div>
      </div>
    </div>
  );
}

export default {ClassName};
