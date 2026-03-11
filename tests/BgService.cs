using System.Text.Json;
using Microsoft.Extensions.Caching.Memory;
using tests.Model;

namespace tests;

public class BgService(IMemoryCache cache, ILogger<BgService> logger) : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        var sqlReq1 = new SqlRequest(20, 10, new Dictionary<string, OrderByClause>
        {
            ["MinPlacement"] = new(1),
            ["BracketId"] = new(2, false)
        }, "test");
        var sqlReq2 = new SqlRequest(20, 10, new Dictionary<string, OrderByClause>
        {
            ["MinPlacement"] = new(1),
            ["BracketId"] = new(2, false)
        }, "test");
        var sqlReq3 = new SqlRequest(30, 20, new Dictionary<string, OrderByClause>
        {
            ["MinPlacement"] = new(1),
            ["BracketId"] = new(2, false)
        }, "test");
        var sqlReq4 = new SqlRequest(20, 10, new Dictionary<string, OrderByClause>
        {
            ["Id"] = new(1, false),
            ["Name"] = new(2)
        }, "test");
        // var sqlReq1 = new SqlRequest(20, 10, "test");
        // var sqlReq2 = new SqlRequest(20, 10, "test");
        // var sqlReq3 = new SqlRequest(30, 20, "test3");
        // var sqlReq4 = new SqlRequest(20, 10, "test4");
        
        logger.LogInformation("req1: {req1}", sqlReq1.ToString());
        logger.LogInformation("req2: {req2}", sqlReq2.ToString());
        logger.LogInformation("req3: {req3}", sqlReq3.ToString());
        logger.LogInformation("req4: {req4}", sqlReq4.ToString());
        logger.LogInformation("Is sqlReq1 equal to sqlReq2? {isEqual}", sqlReq1.ToString() == sqlReq2.ToString()); // True
        logger.LogInformation("Is sqlReq1 equal to sqlReq3? {isEqual}", sqlReq1.ToString() == sqlReq3.ToString()); // False
        logger.LogInformation("Is sqlReq1 equal to sqlReq4? {isEqual}", sqlReq1.ToString() == sqlReq4.ToString()); // False
        logger.LogInformation("Is sqlReq2 equal to sqlReq4? {isEqual}", sqlReq2.ToString() == sqlReq4.ToString()); // False


        cache.Set(sqlReq1.ToString(), "Cached Result 1");
        cache.Set(sqlReq4.ToString(), "Cached Result 4");

        var res = cache.Get(sqlReq2.ToString());
        logger.LogInformation("Cache retrieval for sqlReq2: {result}", res); // Should retrieve "Cached Result 1"


        while (!stoppingToken.IsCancellationRequested)
        {
            await Task.Delay(1000, stoppingToken);
            logger.LogInformation("BgService is running at: {time}", DateTimeOffset.Now);
        }
    }
}