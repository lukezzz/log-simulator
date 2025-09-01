import Icon from '@ant-design/icons';
import type { CustomIconComponentProps } from '@ant-design/icons/lib/components/Icon';
import { createFromIconfontCN } from '@ant-design/icons';

export const LogoSvg = () => (
  <svg width="64" height="64" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">
    <title>Log Simulator App Icon</title>
    <desc>A rounded-square app icon with a log card emitting packets to symbolize simulated logs over TCP/UDP and extensible outputs.</desc>
    <defs>
      <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#0B1B3A" />
        <stop offset="100%" stop-color="#173F86" />
      </linearGradient>
      <linearGradient id="card" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#EAF2FF" />
        <stop offset="100%" stop-color="#BFD2FF" />
      </linearGradient>
      <linearGradient id="net" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#4CB8FF" />
        <stop offset="100%" stop-color="#1E90FF" />
      </linearGradient>
      <linearGradient id="pktA" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#00D3A7" />
        <stop offset="100%" stop-color="#00A37A" />
      </linearGradient>
      <linearGradient id="pktB" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#FFC857" />
        <stop offset="100%" stop-color="#FF9F1C" />
      </linearGradient>
      <filter id="softShadow" x="-50%" y="-50%" width="200%" height="200%">
        <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#000" flood-opacity="0.25" />
      </filter>
      <filter id="glow">
        <feGaussianBlur stdDeviation="2.5" result="b" />
        <feMerge>
          <feMergeNode in="b" />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>
    </defs>
    <rect x="16" y="16" width="480" height="480" rx="96" fill="url(#bg)" />
    <g opacity="0.18" stroke="url(#net)" stroke-width="2">
      <path d="M72,168 L440,168" />
      <path d="M72,256 L440,256" />
      <path d="M72,344 L440,344" />
      <path d="M160,96 L160,416" />
      <path d="M256,96 L256,416" />
      <path d="M352,96 L352,416" />
    </g>
    <g fill="none" stroke="url(#net)" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" opacity="0.9" filter="url(#glow)">
      <rect x="64" y="112" width="40" height="40" rx="8" />
      <rect x="408" y="112" width="40" height="40" rx="8" />
      <rect x="64" y="360" width="40" height="40" rx="8" />
      <rect x="408" y="360" width="40" height="40" rx="8" />
    </g>
    <g filter="url(#softShadow)">
      <rect x="128" y="148" width="256" height="216" rx="18" fill="url(#card)" />
      <rect x="128" y="148" width="10" height="216" rx="6" fill="#8FB3FF" />
      <g fill="#335" opacity="0.8">
        <rect x="156" y="178" width="200" height="14" rx="7" />
        <rect x="156" y="206" width="168" height="12" rx="6" opacity="0.9" />
        <rect x="156" y="232" width="184" height="12" rx="6" opacity="0.9" />
        <rect x="156" y="258" width="144" height="12" rx="6" opacity="0.9" />
        <rect x="156" y="284" width="196" height="12" rx="6" opacity="0.9" />
        <rect x="156" y="310" width="156" height="12" rx="6" opacity="0.9" />
        <rect x="156" y="336" width="188" height="12" rx="6" opacity="0.9" />
      </g>
    </g>

    <g transform="translate(0,0)">
      <path d="M360,256 C392,256 408,256 424,256" stroke="url(#net)" stroke-width="8" stroke-linecap="round" opacity="0.9" />
      <polygon points="392,230 428,246 392,262" fill="url(#pktA)" filter="url(#softShadow)" />
      <polygon points="360,208 404,228 360,248" fill="url(#pktB)" opacity="0.95" filter="url(#softShadow)" />
      <circle cx="444" cy="256" r="10" fill="url(#net)" filter="url(#glow)" />
    </g>
    <g transform="translate(0,6)" opacity="0.9">
      <rect x="196" y="388" width="120" height="12" rx="6" fill="#6EA8FF" />
      <g fill="#6EA8FF">
        <rect x="172" y="404" width="168" height="8" rx="4" />
        <rect x="156" y="416" width="200" height="8" rx="4" opacity="0.8" />
      </g>
    </g>
    <path d="M112,64 C240,40 344,40 400,64 C456,88 472,120 472,120 L472,120 C440,96 280,96 112,120 Z" fill="#FFFFFF" opacity="0.06" />
  </svg>
);

const CustomSVg = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="1em"
    height="1em"
    x="0"
    y="0"
    version="1.1"
    viewBox="0 0 140 140"
    xmlSpace="preserve"
  >
    <image
      width="140"
      height="140"
      x="0"
      y="0"
      href="https://cdn-icons-png.flaticon.com/512/10349/10349752.png"
    ></image>
  </svg>
);


export const LogoIcon = (props: Partial<CustomIconComponentProps>) => (
  <Icon component={LogoSvg} {...props} />
  // <Icon component={CustomSVg} {...props} />
);
