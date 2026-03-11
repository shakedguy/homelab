namespace tests.Model;

public record ParticipationRewardSegmentDataModel
{
    public string Segment { get; set; } = string.Empty;
    public ICollection<ParticipationRewardDataModel> ParticipationRewards { get; set; } = [];
}