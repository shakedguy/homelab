using System.Text;

namespace tests.Model;

public readonly record struct OrderByClause(int Priority = 0, bool IsAscending = true);

public readonly record struct SqlRequest(
    long Limit = 0,
    long Offset = 0,
    IReadOnlyDictionary<string, OrderByClause>? OrderBy = null,
    string? Search = null
)
{
    public override string ToString()
    {
        var sb = new StringBuilder();
        sb.Append($"Limit: {Limit}, Offset: {Offset}");
        if (OrderBy != null && OrderBy.Count > 0)
        {
            sb.Append(", OrderBy: { ");
            foreach (var kvp in OrderBy)
            {
                sb.Append($"{kvp.Key}: (Priority: {kvp.Value.Priority}, IsAscending: {kvp.Value.IsAscending}), ");
            }

            sb.Length -= 2; // Remove trailing comma and space
            sb.Append(" }");
        }

        if (!string.IsNullOrEmpty(Search))
        {
            sb.Append($", Search: \"{Search}\"");
        }

        return sb.ToString();
    }
}