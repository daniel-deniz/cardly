import Image from "next/image";

/** El encuadre se ajusta con object-position para que se le vea la cara. */
export function CardlyAvatar({ size = 32 }: { size?: number }) {
  return (
    <Image
      src="/cardly.jpg"
      alt=""
      width={size}
      height={size}
      priority
      className="shrink-0 rounded-full object-cover ring-1 ring-border-subtle"
      style={{ width: size, height: size, objectPosition: "center 22%" }}
    />
  );
}
