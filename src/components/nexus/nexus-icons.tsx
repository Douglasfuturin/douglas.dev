import type { NexusIconName } from "./nexus-config";

const common = "size-4 shrink-0";

export function NexusIcon({
  name,
  className = common,
}: {
  name: NexusIconName;
  className?: string;
}) {
  switch (name) {
    case "overview":
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
          <path
            d="M4 11.5 12 4l8 7.5V20a1 1 0 0 1-1 1h-5v-6H10v6H5a1 1 0 0 1-1-1v-8.5Z"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinejoin="round"
          />
        </svg>
      );
    case "agents":
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
          <circle cx="9" cy="8" r="3.25" stroke="currentColor" strokeWidth="1.75" />
          <path
            d="M3.5 19c0-3 2.5-5 5.5-5s5.5 2 5.5 5"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinecap="round"
          />
          <path
            d="M16 7.5a2.5 2.5 0 1 1 0 5M14.5 19c.3-2 1.8-3.5 4-3.5"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinecap="round"
          />
        </svg>
      );
    case "orchestrations":
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
          <path
            d="M6 6h12v4H6V6Zm0 8h8v4H6v-4Zm10 0h2v4h-2v-4Z"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinejoin="round"
          />
        </svg>
      );
    case "activity":
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
          <path
            d="M4 18V6M8 18V10M12 18V14M16 18V8M20 18V4"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinecap="round"
          />
        </svg>
      );
    case "studio":
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
          <path
            d="M12 3 4 7v10l8 4 8-4V7l-8-4Z"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinejoin="round"
          />
        </svg>
      );
    case "editor":
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
          <rect
            x="3"
            y="5"
            width="18"
            height="14"
            rx="2"
            stroke="currentColor"
            strokeWidth="1.75"
          />
          <path d="M8 9h8M8 13h5" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
        </svg>
      );
    case "kits":
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
          <path
            d="M12 3 3 8v8l9 5 9-5V8l-9-5Z"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinejoin="round"
          />
        </svg>
      );
    case "pipeline":
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
          <path
            d="M5 12h4l2-4 2 8 2-4h4"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      );
    case "tools":
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
          <path
            d="M14.7 6.3a4 4 0 0 0-5.4 5.4L4 17v3h3l5.3-5.3a4 4 0 0 0 5.4-5.4l-2.1 2.1-1.9-.5-.5-1.9 2.1-2.1Z"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinejoin="round"
          />
        </svg>
      );
    case "plus":
    default:
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
          <path
            d="M12 5v14M5 12h14"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinecap="round"
          />
        </svg>
      );
  }
}
