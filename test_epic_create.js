const PanelView = require('./src/panel/panel_view');

async function test() {
    const panel = new PanelView('./bots/story_bot');
    
    try {
        console.log('=== Query initial graph ===');
        const r1 = await panel.execute('story_graph');
        const data1 = (r1.result || r1);
        console.log('Initial epic count:', data1.epics.length);
        console.log('Initial epics:', data1.epics.map(e => e.name).slice(0, 3));
        
        console.log('\n=== Test command format 1: story_graph.create_epic."Name" ===');
        const r2 = await panel.execute('story_graph.create_epic."TestEpic789"');
        const data2 = typeof r2 === 'string' ? JSON.parse(r2) : r2;
        console.log('Create result status:', data2.status);
        console.log('Create result message:', data2.message);
        
        console.log('\n=== Query after create ===');
        const r3 = await panel.execute('story_graph');
        const data3 = (r3.result || r3);
        console.log('Final epic count:', data3.epics.length);
        const found = data3.epics.find(e => e.name === 'TestEpic789');
        console.log('TestEpic789 found:', found ? 'YES' : 'NO');
        
    } catch (e) {
        console.error('Error:', e.message);
    } finally {
        panel.cleanup();
    }
}

test();
