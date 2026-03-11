using Microsoft.EntityFrameworkCore;

namespace tests.Model;

[Owned]
public record ParticipationRewardDataModel
{
    public int Tier { get; set; }
    public int Points { get; set; }
    public string Reward { get; set; } = string.Empty;
}