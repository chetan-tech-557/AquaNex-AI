import Image from 'next/image'
import { Fish, Leaf, Sprout } from 'lucide-react'

const bubbles = [
  { left: '4%', size: 8, duration: 14, delay: 0 },
  { left: '11%', size: 14, duration: 18, delay: 4 },
  { left: '19%', size: 6, duration: 12, delay: 7 },
  { left: '27%', size: 10, duration: 16, delay: 2 },
  { left: '36%', size: 5, duration: 11, delay: 9 },
  { left: '44%', size: 12, duration: 20, delay: 5 },
  { left: '53%', size: 7, duration: 13, delay: 1 },
  { left: '61%', size: 16, duration: 22, delay: 8 },
  { left: '69%', size: 6, duration: 12, delay: 3 },
  { left: '77%', size: 11, duration: 17, delay: 10 },
  { left: '85%', size: 8, duration: 15, delay: 6 },
  { left: '93%', size: 13, duration: 19, delay: 2 },
]

const fishes = [
  { top: '18%', size: 28, duration: 38, delay: 0, reverse: false, color: 'text-primary/35' },
  { top: '34%', size: 18, duration: 46, delay: 12, reverse: true, color: 'text-accent/30' },
  { top: '52%', size: 36, duration: 55, delay: 6, reverse: false, color: 'text-primary/25' },
  { top: '68%', size: 22, duration: 42, delay: 20, reverse: true, color: 'text-primary/30' },
  { top: '80%', size: 16, duration: 34, delay: 3, reverse: false, color: 'text-accent/35' },
]

const plants = [
  { left: '2%', size: 72, delay: 0, Icon: Sprout },
  { left: '9%', size: 52, delay: 1.5, Icon: Leaf },
  { left: '82%', size: 64, delay: 0.8, Icon: Sprout },
  { left: '91%', size: 84, delay: 2.2, Icon: Leaf },
]

export function OceanBackground() {
  return (
    <div aria-hidden="true" className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      <Image src="/images/underwater-bg.png" alt="" fill priority sizes="100vw" className="object-cover" />
      <div className="absolute inset-0 bg-gradient-to-b from-[oklch(0.17_0.05_235/0.55)] via-[oklch(0.17_0.05_240/0.72)] to-[oklch(0.14_0.05_240/0.9)]" />

      <div className="absolute -top-20 left-[15%] h-[80vh] w-40 animate-rays bg-gradient-to-b from-white/25 to-transparent blur-2xl" />
      <div
        className="absolute -top-20 left-[45%] h-[70vh] w-24 animate-rays bg-gradient-to-b from-white/20 to-transparent blur-2xl"
        style={{ animationDelay: '3s' }}
      />
      <div
        className="absolute -top-20 left-[72%] h-[85vh] w-32 animate-rays bg-gradient-to-b from-white/20 to-transparent blur-2xl"
        style={{ animationDelay: '6s' }}
      />

      {fishes.map((f, i) => (
        <div
          key={i}
          className="absolute left-0 animate-swim"
          style={{
            top: f.top,
            animationDuration: `${f.duration}s`,
            animationDelay: `-${f.delay}s`,
            animationDirection: f.reverse ? 'reverse' : 'normal',
          }}
        >
          <div className="animate-bob" style={{ animationDelay: `${i * 0.6}s` }}>
            <Fish
              className={f.color}
              style={{ width: f.size, height: f.size, transform: f.reverse ? 'scaleX(-1)' : undefined }}
            />
          </div>
        </div>
      ))}

      {bubbles.map((b, i) => (
        <span
          key={i}
          className="absolute bottom-[-20px] animate-bubble rounded-full border border-white/40 bg-white/10"
          style={{
            left: b.left,
            width: b.size,
            height: b.size,
            animationDuration: `${b.duration}s`,
            animationDelay: `-${b.delay}s`,
          }}
        />
      ))}

      {plants.map(({ left, size, delay, Icon }, i) => (
        <div key={i} className="absolute bottom-0 animate-sway" style={{ left, animationDelay: `${delay}s` }}>
          <Icon className="text-accent/25" style={{ width: size, height: size }} />
        </div>
      ))}
    </div>
  )
}
