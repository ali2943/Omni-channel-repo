interface Props {
  status: string;
}

const styles: Record<string, string> = {
  open: 'bg-yellow-100 text-yellow-800',
  in_progress: 'bg-blue-100 text-blue-800',
  closed: 'bg-green-100 text-green-800',
};

export default function StatusBadge({ status }: Props) {
  const cls = styles[status] ?? 'bg-gray-100 text-gray-800';
  const label = status.replace('_', ' ');
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${cls}`}>
      {label}
    </span>
  );
}
