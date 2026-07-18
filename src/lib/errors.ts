type PostgresError = {
  code?: string;
  message?: string;
  details?: string;
};

function traducirError(error: PostgresError): string | null {
  switch (error?.code) {
    case "23505":
      return "Ya existe un registro con ese mismo valor.";
    case "23502":
      return "Falta rellenar un campo obligatorio.";
    case "23503":
      return "No se puede completar la operación porque hay datos relacionados que dependen de este registro.";
    case "22P02":
      return "Uno de los valores introducidos no tiene el formato correcto.";
    default:
      return null;
  }
}

export function dbError(error: PostgresError): never {
  console.error("[Supabase]", error);
  throw new Error(
    traducirError(error) ||
      error?.message ||
      "Ha ocurrido un error al guardar los datos. Inténtalo de nuevo."
  );
}
