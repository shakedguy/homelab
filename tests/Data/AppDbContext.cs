using Microsoft.EntityFrameworkCore;
using tests.Model;

namespace tests.Data;

public class AppDbContext : DbContext
{
    public DbSet<MTX_TournamentV2SegmentData> MTX_TournamentV2SegmentData { get; set; }


    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options)
    {
    }
}